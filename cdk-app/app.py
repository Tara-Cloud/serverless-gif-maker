#!/usr/bin/env python3
import aws_cdk as cdk

from cdk_app.gif_splitter_infra_stack import GifSplitterInfraStack
from cdk_app.static_s3_website_stack import StaticS3Stack
from cdk_app.datadog_stack import DatadogStack

app = cdk.App()
datadog_stack = DatadogStack(app, "DatadogCDKStack", env=cdk.Environment(region="us-east-1"))
infra_stack = GifSplitterInfraStack(
    app,
    "GifSplitterInfraStack",
    env=cdk.Environment(region="us-east-1"),
    datadog_secret=datadog_stack.datadog_secret,
    datadog=datadog_stack.datadog,
)
StaticS3Stack(
    app,
    "S3WebsiteStack",
    gif_bucket=infra_stack.gif_output_bucket,
    env=cdk.Environment(region="us-east-1"),
    datadog_secret=datadog_stack.datadog_secret,
    datadog=datadog_stack.datadog,
)

app.synth()
