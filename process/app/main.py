from flask import Flask

import json
import os
import time

from google.cloud import pubsub_v1
from google.cloud import bigquery
from google.cloud.exceptions import NotFound, Conflict


app = Flask(__name__)

@app.route('/')
def ok():
    return 'ok'

# Dummy handler for App Engine request sent on startup
@app.route('/_ah/start')
def start_app():
    return 'App Starting'

# Dummy handler for App Engine request sent on shutdown
@app.route('/_ah/stop')
def stop_app():
    return 'App Stopping'

def subscribe():
    future = subscriber.subscribe(subscription_path, callback=callback)

    # The subscriber is non-blocking, so we must keep the main thread from
    # exiting to allow it to process messages in the background.
    print('Listening for messages on {} ...'.format(subscription_path))
    loop = True
    while loop:
        time.sleep(1)

def callback(message):
    if message.data:
        decoded_message = message.data.decode('utf-8')
        rows_to_insert = json.loads(decoded_message)

        try:
            table = bq_client.get_table(table_ref)
        except NotFound:
            create_table()
            table = bq_client.get_table(table_ref)

        print("Inserting {} rows into BigQuery ...".format(len(rows_to_insert)))
        errors = bq_client.insert_rows(table, rows_to_insert)
        if errors != []:
            print(errors)
        else:
            message.ack()

    assert errors == []

def create_table():
    schema = [
        bigquery.SchemaField("ModeName", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Timing", 'RECORD', fields=(
            bigquery.SchemaField("Sent", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("Read", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("Received", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("Insert", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("Source", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("CountdownServerAdjustment", "TIME", mode="NULLABLE")
        )),
        bigquery.SchemaField("Towards", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("TimeToStation", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("ExpectedArrival", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("Timestamp", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("DestinationName", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("PlatformName", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("LineName", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("LineId", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("NaptanId", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("DestinationNaptanId", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Id", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("StationName", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("TimeToLive", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("Bearing", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Direction", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("CurrentLocation", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("VehicleId", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("OperationType", "INTEGER", mode="NULLABLE")
    ]


    table = bigquery.Table(table_ref, schema=schema)
    try:
        bq_client.get_table(table)
    except NotFound:
        try:
            table = bq_client.create_table(table)
            print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))
            print("Going to sleep for 90 seconds to ensure data availability in newly created table")
            time.sleep(90)
        except Conflict:
            pass

    return

@app.errorhandler(500)
def server_error(e):
    print('An internal error occurred')
    return 'An internal error occurred.', 500

print("Preparing..")
project_id = os.getenv('PROJECT')
subscription_name = os.getenv('SUBSCRIPTION')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

dataset_id = os.getenv('DATASET')
table_id = os.getenv('TABLE')

bq_client = bigquery.Client()
table_ref = bq_client.dataset(dataset_id).table(table_id)

subscribe()
