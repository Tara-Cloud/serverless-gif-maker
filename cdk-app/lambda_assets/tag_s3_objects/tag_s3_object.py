import boto3
import os
import json

s3 = boto3.client("s3")
GIF_BUCKET = os.environ.get("GIF_BUCKET")


def tag_s3_object(bucket_name, object_key, tags):
    try:
        print(f"Tagging {object_key} in {bucket_name} with {tags}")
        s3 = boto3.client("s3")
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
    tags = json.loads(event["body"]).get("tags")
    s3_key = json.loads(event["body"]).get("s3_key")
    # tags = [
    #     {'Key': 'Tag1', 'Value': 'Value1'},
    #     {'Key': 'Tag2', 'Value': 'Value2'},
    #     # ... add more tags as needed
    # ]

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