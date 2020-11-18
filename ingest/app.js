'use strict';

const express = require('express');
const Ably = require('ably');
const {PubSub} = require('@google-cloud/pubsub');
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');

const app = express();
const projectId = process.env.PROJECT;
const pubSub = new PubSub({projectId});
const secretManager = new SecretManagerServiceClient({projectId});

async function forwardMessages(
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

  console.log('Subscribing to Ably TfL...');
  channel.subscribe(async function(message) {
    let buf = Buffer.from(JSON.stringify(message.data));
    console.log(`Forwarding ${message.data.length} records to Pub/Sub`);
    const messageId = await pubSub
      .topic(topicName)
      .publish(buf);
  });
}

app.get('/', (req, res) => {
  res.status(200).send('ok').end();
});

// Dummy handler for App Engine request sent on startup
app.get('/_ah/start', (req, res) => {
  res.status(200).send('App Starting').end();
});

// Dummy handler for App Engine request sent on shutdown
app.get('/_ah/stop', (req, res) => {
  res.status(200).send('App Stopping').end();
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}`);
});

forwardMessages();
