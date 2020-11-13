const Ably = require('ably');
const {PubSub} = require('@google-cloud/pubsub');
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');

const projectId = process.env.PROJECT;
const pubSub = new PubSub({projectId});
const secretManager = new SecretManagerServiceClient({projectId});

async function main(
  topicName = process.env.TOPIC,
  subscriptionName = process.env.SUBSCRIPTION
) {
  const ablyApiKeySecretRef = `projects/${projectId}/secrets/ABLY_API_KEY/versions/latest`
  const [ablyApiKeySecret] = await secretManager.accessSecretVersion({
    name: ablyApiKeySecretRef
  });
  const ablyApiKey = ablyApiKeySecret.payload.data.toString('utf8');

  const ablyClient = new Ably.Realtime(ablyApiKey);
  const channelName = '[product:ably-tfl/tube]tube:jubilee:940GZZLUWYP:arrivals';
  const channel = ablyClient.channels.get(channelName);

  channel.subscribe(async function(message) {
    let buf = Buffer.from(JSON.stringify(message.data));
    console.log(`Forwarding ${message.data.length} records to Pub/Sub`);
    const messageId = await pubSub
      .topic(topicName)
      .publish(buf);
  });
}

main();
