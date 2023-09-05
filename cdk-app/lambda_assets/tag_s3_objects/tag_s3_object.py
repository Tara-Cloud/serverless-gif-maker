import boto3
import os
import json
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
GIF_BUCKET = os.environ.get("GIF_BUCKET")


def tag_s3_object(bucket_name, object_key, tags_to_add):
    try:
        s3 = boto3.client("s3")
        tags = []
        tags.append(tags_to_add)
        print(f"Tagging {object_key} in {bucket_name} with {tags}")
        s3.put_object_tagging(
            Bucket=bucket_name, Key=object_key, Tagging={"TagSet": tags}
        )
        return "Tags added successfully"
    except Exception as e:
        return str(e)


# Example usage:
# You can call the function with the bucket name, object key and a list of tags (as dictionaries) as arguments.
# tags should be a list of dictionaries with 'Key' and 'Value' as keys.
def handler(event, context):
    try:
        tags = json.loads(event["body"]).get("tags")
        s3_key = json.loads(event["body"]).get("s3_key")

        response = tag_s3_object(GIF_BUCKET, s3_key, tags)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
                "Cache-Control": "no-store",
            },
            "body": json.dumps({"response": response}),
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
