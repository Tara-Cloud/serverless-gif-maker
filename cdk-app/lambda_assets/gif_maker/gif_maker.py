import json
import boto3
#import urllib.parse
import subprocess
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET') #bucket to write finished gif to

def handler(event, context):
    #get object key and desired timestamp from event
    print(event)
    bucket = event['detail']['bucket']
    key = event['detail']['key']
    start_at = event['detail']['start_at']
    duration = event['detail']['duration']

    #get presigned url for mp4 file
    presigned_url = create_presigned_url(bucket, key, 180)

    #make gif
    end_at = float(start_at) + float(duration)
    gif_name = f'{key.removesuffix(".mp4")}.{start_at}-{end_at}'
    make_gif(presigned_url, start_at, duration, gif_name)

    #write gif to s3
    write_gif_to_s3(OUTPUT_BUCKET, key, gif_name)
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully wrote {gif_name}.gif to {OUTPUT_BUCKET}.')
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
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                            ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def make_gif(mp4_url, start_at, duration, gif_name):
    os.chdir('/tmp')
    result = subprocess.run(
        ['ffmpeg', '-ss', str(start_at), '-t', str(duration), '-i', str(mp4_url), '-f', 'gif', f'{gif_name}.gif'], 
        stdout=subprocess.PIPE,
        universal_newlines=True)
    return

def write_gif_to_s3(output_bucket, original_key, gif_name):
    new_key = f'{original_key.removesuffix(".mp4")}/{gif_name}.gif'
    try:
        response = s3.upload_file(f'/tmp/{gif_name}.gif', output_bucket, new_key)
    except ClientError as e:
        logging.error(e)
        return None
    return True
