import boto3
import json
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

GIF_BUCKET = os.environ.get("GIF_BUCKET")


def handler(event, context):
    try:
        s3_key = json.loads(event["body"]).get("s3_key")
        tags = []
        # use boto3 to get tags from s3 object
        response = s3.get_object_tagging(
            Bucket=GIF_BUCKET,
            Key=s3_key,
        )
        for tag in response["TagSet"]:
            tags.append({"Key": tag["Key"], "Value": tag["Value"]})

        print(f"Tags for {s3_key}: {tags}")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
                "Cache-Control": "no-store",
            },
            "body": json.dumps({"Tags": tags}),
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
