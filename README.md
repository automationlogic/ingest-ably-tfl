# Ingest Ably TfL

## Overview

The ingestion process fetches a subset of the TfL data through Ably [online source](https://www.ably.io/hub/ably-tfl/tube) as part of a proof of concept data ingestion use case. It runs as 2 App Engine apps, one of which handles both fetching the data and forwarding it to Pub/Sub (this app), the other reads it from Pub/Sub and inserts it into BigQuery ([Process Ably TFL](https://github.com/automationlogic/process-ably-tfl)).

## Prerequisites

1. [Platform bootstrap](https://github.com/automationlogic/platform-bootstrap)
2. [Analytics infra](https://github.com/automationlogic/analytics-infra)

## Configuration

The app configuration resides in a `app.yaml` template called `app.yaml.tmpl`. The reason for the template is to allow Cloud Build to inject environment variables into the configuration file if needed.

```
PROJECT: $ANALYTICS_PROJECT    # replace in cloud build step
TOPIC: ably-tfl-tube
SUBSCRIPTION: ably-tfl-tube
DATASET: ably_tfl
TABLE: tube
```

The `$ANALYTICS_PROJECT` environment variable is a pipeline substitution in the pipeline trigger. It is injected as part of a Cloud Build step:

`sed -e "s/\$$ANALYTICS_PROJECT/$_ANALYTICS_PROJECT/g" app.yaml.tmpl > app.yaml`

It is passed through from the [Platform Bootstrap](https://github.com/automationlogic/platform-bootstrap) process, which is where it is originally configured.

The app accesses an API key stored in GCP Secret Manager within the entry called `ABLY_API_KEY`. The code relies on the `<$ANALYTICS_PROJECT>@appspot.gserviceaccount.com` user having the `Secret Manager Secret Accessor` permission.

## Run

The pipeline is automatically triggered when code is pushed. It can also be triggered manually via the console.
