from aws_cdk import Stack, aws_secretsmanager as secretsmanager
from constructs import Construct

from datadog_cdk_constructs_v2 import Datadog


class DatadogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # datadog api key secret
        # pass to datadog construct to configure lambda execution roles
        datadog_secret = secretsmanager.Secret.from_secret_complete_arn(
            self, "secret", secret_complete_arn=self.node.try_get_context("DD_API_KEY_SECRET_ARN")
        )

        # datadog construct
        self.datadog = Datadog(
            self,
            "Datadog",
            api_key_secret=datadog_secret,
            env="tara-cloud",
            service="gif-splitter",
            add_layers=True,
            python_layer_version=78,
            extension_layer_version=47,
            flush_metrics_to_logs=True,
            site="datadoghq.com",
            enable_datadog_tracing=True,
            enable_datadog_logs=True,
            source_code_integration=True,
            log_level="DEBUG",
        )

        self.datadog_secret = datadog_secret
