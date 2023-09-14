import boto3
import os
import json
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
GIF_BUCKET = os.environ.get("GIF_BUCKET")
ARCHIVE_BUCKET = os.environ.get("ARCHIVE_BUCKET")
STORAGE_CLASS = os.environ.get("STORAGE_CLASS")


def archive_object(object_key):
    try:
        response = s3.copy_object(
            Bucket=ARCHIVE_BUCKET,
            CopySource={"Bucket": GIF_BUCKET, "Key": object_key},
            Key=object_key,
            StorageClass=STORAGE_CLASS,
        )
        return response
    except Exception as e:
        return str(e)


def delete_object(object_key):
    try:
        response = s3.delete_object(
            Bucket=GIF_BUCKET,
            Key=object_key,
        )
        return response
    except Exception as e:
        return str(e)


def handler(event, context):
    try:
        s3_key = json.loads(event["body"]).get("s3_key")
        archive_response = archive_object(s3_key)
        delete_response = delete_object(s3_key)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
                "Cache-Control": "no-store",
            },
            "body": json.dumps(f"{archive_response} {delete_response}"),
        }
    except ClientError as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
                "Cache-Control": "no-store",
            },
            "body": json.dumps({"error": "Internal Server Error"}),
        }
