import boto3
import json
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
GIF_BUCKET = os.environ.get("GIF_BUCKET")


def handler(event, context):
    presigned_urls = []
    gif_keys = json.loads(event["body"]).get("gifKeys")
    for gif_key in gif_keys:
        presigned_url = create_presigned_url(GIF_BUCKET, gif_key, 180)
        presigned_urls.append(presigned_url)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
            "Cache-Control": "no-store",
        },
        "body": json.dumps({"presignedUrls": presigned_urls}),
    }


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
