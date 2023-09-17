from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
)
from constructs import Construct
from datadog_cdk_constructs_v2 import Datadog
import os


class StaticS3Stack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        gif_bucket: s3.Bucket,
        datadog_secret: secretsmanager.Secret,
        datadog: Datadog,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # s3 bucket to host React website
        website_bucket = s3.Bucket(
            self,
            "website_bucket",
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(restrict_public_buckets=False),
            website_index_document="index.html",
        )

        website_bucket.grant_public_access()

        # deploy static web assets to bucket
        static_assets_path = "../web-ui/dist/"
        s3_deploy.BucketDeployment(
            self,
            "s3_deployment",
            destination_bucket=website_bucket,
            sources=[s3_deploy.Source.asset(path=static_assets_path)],
        )

        # s3 bucket to archive gifs
        gif_archive_bucket = s3.Bucket(self, "gif_archive_bucket")

        # set up cloudfront distribution for gif_bucket
        access_identity = cloudfront.OriginAccessIdentity(self, "access_identity")
        cloudfront.Distribution(
            self,
            "cloudfront_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket=gif_bucket, origin_access_identity=access_identity)
            ),
        )

        # lambda function to generate pre-signed-urls
        cwd = os.getcwd()
        presigned_url_lambda = _lambda.Function(
            self,
            "gif_presigned_urls",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="presigned_url.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/generate_presigned_url")),
            timeout=Duration.seconds(180),
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "GIF_BUCKET": gif_bucket.bucket_name,
                # TODO: change this to your own domain
                "CORS_ORIGIN": website_bucket.bucket_website_url,
            },
        )
        gif_bucket.grant_read(presigned_url_lambda)

        get_s3_keys_lambda = _lambda.Function(
            self,
            "list_s3_keys",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="list_s3_keys.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/list_s3_keys")),
            timeout=Duration.seconds(180),
            environment={
                "GIF_BUCKET": gif_bucket.bucket_name,
                "PAGE_SIZE": "20",
                # TODO: change this to your own domain
                "CORS_ORIGIN": website_bucket.bucket_website_url,
            },
        )
        gif_bucket.grant_read(get_s3_keys_lambda)

        tag_s3_objects_lambda = _lambda.Function(
            self,
            "tag_s3_objects",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="tag_s3_object.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/tag_s3_objects")),
            timeout=Duration.seconds(180),
            environment={
                "GIF_BUCKET": gif_bucket.bucket_name,
                "CORS_ORIGIN": website_bucket.bucket_website_url,
            },
        )
        tag_s3_objects_lambda.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["s3:PutObjectTagging"],
                resources=[f"{gif_bucket.bucket_arn}/*"],
            )
        )

        archive_gifs_lambda = _lambda.Function(
            self,
            "archive_gifs",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="archive_gif.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/archive_gif")),
            timeout=Duration.seconds(180),
            environment={
                "GIF_BUCKET": gif_bucket.bucket_name,
                "CORS_ORIGIN": website_bucket.bucket_website_url,
                "ARCHIVE_BUCKET": gif_archive_bucket.bucket_name,
                "STORAGE_CLASS": "STANDARD_IA",
            },
        )
        gif_bucket.grant_read(archive_gifs_lambda)
        gif_bucket.grant_delete(archive_gifs_lambda)
        gif_archive_bucket.grant_put(archive_gifs_lambda)

        get_gif_tags_lambda = _lambda.Function(
            self,
            "get_gif_tags",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="get_gif_tags.handler",
            code=_lambda.Code.from_asset(os.path.join(cwd, "lambda_assets/get_gif_tags")),
            timeout=Duration.seconds(180),
            environment={
                "GIF_BUCKET": gif_bucket.bucket_name,
                "CORS_ORIGIN": website_bucket.bucket_website_url,
            },
        )
        gif_bucket.grant_read(get_gif_tags_lambda)

        # api to front presigned url lambda
        api_log_group = logs.LogGroup(self, "GifApiLogGroup", removal_policy=RemovalPolicy.DESTROY)
        api = apigw.LambdaRestApi(
            self,
            "presigned_url_api",
            handler=presigned_url_lambda,
            proxy=False,
            description="This service serves pre-signed urls for gif files",
            cloud_watch_role=True,
            deploy_options=apigw.StageOptions(
                access_log_destination=apigw.LogGroupLogDestination(api_log_group),
                logging_level=apigw.MethodLoggingLevel.INFO,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=[website_bucket.bucket_website_url],
                allow_methods=["GET", "POST", "OPTIONS"],
            ),
        )

        gif_url = api.root.add_resource("gif_url")
        gif_url.add_method(
            "POST",
        )

        list_s3_keys = api.root.add_resource("list_s3_keys")

        list_s3_keys.add_method(
            "POST",
            integration=apigw.LambdaIntegration(get_s3_keys_lambda),
        )

        tag_s3_object = api.root.add_resource("tag_gif")
        tag_s3_object.add_method("POST", integration=apigw.LambdaIntegration(tag_s3_objects_lambda))

        archive_gif = api.root.add_resource("archive_gif")
        archive_gif.add_method("POST", integration=apigw.LambdaIntegration(archive_gifs_lambda))

        get_tags = api.root.add_resource("get_tags")
        get_tags.add_method("POST", integration=apigw.LambdaIntegration(get_gif_tags_lambda))

        datadog.add_lambda_functions(
            [presigned_url_lambda, get_s3_keys_lambda, tag_s3_objects_lambda, archive_gifs_lambda, get_gif_tags_lambda]
        )

        # grant read on data dog secret to each lambda
        datadog_secret.grant_read(presigned_url_lambda)
        datadog_secret.grant_read(get_s3_keys_lambda)
        datadog_secret.grant_read(tag_s3_objects_lambda)
        datadog_secret.grant_read(archive_gifs_lambda)
        datadog_secret.grant_read(get_gif_tags_lambda)

        # output url for s3 bucket
        CfnOutput(
            self,
            "url_output",
            value=website_bucket.bucket_website_url,
            description="S3 Website URL",
        )
