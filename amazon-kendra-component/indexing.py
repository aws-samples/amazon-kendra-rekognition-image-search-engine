import json
import os
import boto3

KENDRA = boto3.client("kendra")
INDEX_ID = os.environ["INDEX_ID"]
DS_ID = os.environ["DS_ID"]


def lambda_handler(event, context):
    dbRecords = event["Records"]

    # Loop through items from Amazon DynamoDB
    for row in dbRecords:
        rowData = row["dynamodb"]["NewImage"]
        originUrl = rowData["OriginURL"]["S"]
        publishedDate = rowData["PublishDate"]["S"]
        architectureUrl = rowData["ArchitectureURL"]["S"]
        title = rowData["Title"]["S"]

        metadata = rowData["Metadata"]["M"]
        crawlerMetadata = metadata["crawler"]["S"]
        rekognitionMetadata = metadata["Rekognition"]["M"]
        rekognitionLabels = rekognitionMetadata["labels"]["S"]
        rekognitionServices = rekognitionMetadata["textServices"]["S"]

        concatenatedText = (
            f"{crawlerMetadata} {rekognitionLabels} {rekognitionServices}"
        )

        add_document(
            dsId=DS_ID,
            indexId=INDEX_ID,
            originUrl=originUrl,
            architectureUrl=architectureUrl,
            title=title,
            publishedDate=publishedDate,
            text=concatenatedText,
        )

    return


# Function to add the diagram into Kendra index
def add_document(dsId, indexId, originUrl, architectureUrl, title, publishedDate, text):
    document = get_document(
        dsId, indexId, originUrl, architectureUrl, title, publishedDate, text
    )
    documents = [document]
    result = KENDRA.batch_put_document(IndexId=indexId, Documents=documents)
    print("result:" + json.dumps(result))
    return True


# Frame the diagram into a document that Kendra accepts
def get_document(dsId, originUrl, architectureUrl, title, publishedDate, text):
    document = {
        "Id": originUrl,
        "Title": title,
        "Attributes": [
            {"Key": "_data_source_id", "Value": {"StringValue": dsId}},
            {"Key": "_source_uri", "Value": {"StringValue": architectureUrl}},
            {"Key": "_created_at", "Value": {"DateValue": publishedDate}},
            {"Key": "publish_date", "Value": {"DateValue": publishedDate}},
        ],
        "Blob": text,
    }

    return document
