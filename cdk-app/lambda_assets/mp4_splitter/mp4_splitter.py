import json
import boto3
import urllib.parse
import subprocess
import os
import math
from botocore.exceptions import ClientError
import logging

s3 = boto3.client("s3")
events = boto3.client("events")
GIF_DURATION_SECONDS = os.environ.get("DESIRED_DURATION_IN_SECONDS")
EVENT_BUS_NAME = os.environ.get("EVENT_BUS_NAME")


def handler(event, context):
    # get mp4 object
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    # get mp4 duration using presigned s3 url
    presigned_url = create_presigned_url(bucket, key, 180)
    video_duration = math.floor(float(get_video_duration(presigned_url)))  # returns duration in seconds
    print(f"video length: {video_duration} seconds")
    put_gif_maker_events(bucket, key, video_duration)

    return {"statusCode": 200, "body": json.dumps(f"Successfully processed {key}")}


# def ffmpeg_version():
#     p = subprocess.Popen(["ffmpeg", "-version"], stdout=subprocess.PIPE)
#     out = p.stdout.read()
#     print("Output: ")
#     print(out)


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": object_name}, ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def get_video_duration(url):
    # fmt: off
    # ffprobe = subprocess.run(['ffprobe', '-loglevel', 'error', '-show_streams', str(url), '-print_format', 'json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # noqa E501
    # fmt: on

    duration = subprocess.run(
        [
            "ffprobe",
            "-i",
            str(url),
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=%s" % ("p=0"),
        ],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    return duration.stdout


def put_gif_maker_events(bucket, key, mp4_duration):
    entries = []
    for i in range(0, mp4_duration - 1):
        entry_details = json.dumps({"bucket": bucket, "key": key, "start_at": i, "duration": GIF_DURATION_SECONDS})
        entries.append(
            {
                "Source": "lambda.mp4split",
                "DetailType": "newVideoUpload",
                "Detail": entry_details,
                "EventBusName": EVENT_BUS_NAME,
            },
        )

    batch_size = 10
    batches = [entries[i : i + batch_size] for i in range(0, len(entries), batch_size)]  # noqa E203

    for batch in batches:
        response = events.put_events(Entries=batch)
        print(response)
    return
