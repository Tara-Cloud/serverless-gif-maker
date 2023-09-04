import boto3
import json
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
paginator = s3.get_paginator("list_objects_v2")

GIF_BUCKET = os.environ.get("GIF_BUCKET")
PAGE_SIZE = int(os.environ.get("PAGE_SIZE"))


def handler(event, context):
    try:
        objects = []
        continuation_token = None
        next_token = None

        # Check for continuation token
        if "continuationToken" in event["body"]:
            continuation_token = json.loads(event["body"]).get("continuationToken")
            print(f"Using continuation token: {continuation_token}")

        pagination_config = {"MaxItems": PAGE_SIZE}
        if continuation_token:
            pagination_config["StartingToken"] = continuation_token

        print(pagination_config)
        page_iterator = paginator.paginate(
            Bucket=GIF_BUCKET, PaginationConfig=pagination_config
        )

        for page in page_iterator:
            if "Contents" in page:
                for item in page["Contents"]:
                    objects.append(item["Key"])
                print(page)

            if "NextContinuationToken" in page:
                next_token = page["NextContinuationToken"]

        print(objects)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
                "Cache-Control": "no-store",
            },
            "body": json.dumps({"s3_keys": objects, "next_token": next_token}),
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
