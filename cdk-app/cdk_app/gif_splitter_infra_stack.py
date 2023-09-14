from aws_cdk import (
    Duration,
    Size,
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
import os


class GifSplitterInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # use existing source and destination s3 buckets
        mp4_input_bucket = s3.Bucket.from_bucket_arn(self, "input_bucket", bucket_arn="arn:aws:s3:::tc-test-gif-input")
        self.gif_output_bucket = s3.Bucket.from_bucket_arn(
            self, "output_bucket", bucket_arn="arn:aws:s3:::tc-test-gif-output"
        )

        self.gif_output_bucket

        # lambda functions
        cwd = os.getcwd()

        ffmpeg_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "ffmpeg_layer", "arn:aws:lambda:us-east-1:112825984205:layer:ffmpeg:1"
        )

        event_bus = events.EventBus(self, "gif_maker_bus", event_bus_name="gif_maker_bus")
        mp4_splitter = _lambda.Function(
            self,
            "splitter_function",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="mp4_splitter.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/mp4_splitter")),
            timeout=Duration.seconds(180),
            environment={
                "DESIRED_DURATION_IN_SECONDS": "2",
                "EVENT_BUS_NAME": event_bus.event_bus_name,
            },
            layers=[ffmpeg_layer],
        )

        gif_maker = _lambda.Function(
            self,
            "gif_maker",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="gif_maker.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/gif_maker")),
            timeout=Duration.seconds(180),
            environment={"OUTPUT_BUCKET": self.gif_output_bucket.bucket_name},
            layers=[ffmpeg_layer],
            ephemeral_storage_size=Size.mebibytes(10000),
        )

        # event bus and rule to target gif maker lambda
        event_bus.grant_all_put_events(mp4_splitter)
        rule = events.Rule(
            self,
            "gif_lambda_rule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(source=["lambda.mp4split"], detail_type=["newVideoUpload"]),
        )
        rule.add_target(targets.LambdaFunction(gif_maker, retry_attempts=3))

        # grant read permission to upload bucket and add lambda trigger for mp4 files
        mp4_input_bucket.grant_read(mp4_splitter)
        mp4_input_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(mp4_splitter),
            s3.NotificationKeyFilter(suffix=".mp4"),
        )

        # grant neccesary read and write permissions to gif maker lambda
        mp4_input_bucket.grant_read(gif_maker)
        self.gif_output_bucket.grant_write(gif_maker)
