#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_app.gif_splitter_infra_stack import GifSplitterInfraStack
from cdk_app.static_s3_website_stack import StaticS3Stack

app = cdk.App()
infra_stack = GifSplitterInfraStack(
    app,
    "GifSplitterInfraStack",
    env=cdk.Environment(region="us-east-1"),
)
StaticS3Stack(
    app,
    "S3WebsiteStack",
    gif_bucket=infra_stack.gif_output_bucket,
    env=cdk.Environment(region="us-east-1"),
)

app.synth()
