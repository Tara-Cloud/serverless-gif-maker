from aws_cdk import Stack, aws_secretsmanager as secretsmanager
from constructs import Construct

# from datadog_cdk_constructs_v2 import Datadog


class DatadogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # datadog api key secret
        # pass to datadog construct to configure lambda execution roles
        datadog_api_key_secret = secretsmanager.Secret.from_secret_partial_arn(
            self,
            "dd_api_key_secret",
            secret_partial_arn="""arn:aws:secretsmanager:us-east-1:112825984205:
        secret:DdApiKeySecret-KX38ECVTR2uT-mxkSag""",
        )

        # datadog construct
        # datadog = Datadog(
        # self,
        # "Datadog",
        # api_key_secret_arn=datadog_api_key_secret.secret_arn,
        # env="tara-cloud",
        # service="gif-splitter",
        # add_layers=True,
        # python_layer_version=78,
        # extension_layer_version=47,
        # flush_metrics_to_logs=True,
        # site="datadoghq.com",
        # enable_datadog_tracing=True,
        # enable_datadog_logs=True,
        # source_code_integration=True,
        # log_level="DEBUG",
        # )

        self.datadog_secret = datadog_api_key_secret
