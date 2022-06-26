from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_logs as logs,
    aws_logs_destinations as destinations,
    aws_sns_subscriptions as snsSubs,
    CfnParameter,
)
from constructs import Construct


class LambdaCloudwatchPatternNotificationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creates SNS topic
        sns_topic = sns.Topic(self, "EmailNotification")
        # Accepts email address as parameter
        email_address = CfnParameter(self, "email")
        # Creates the email subscription
        sns_topic.add_subscription(
            snsSubs.EmailSubscription(email_address.value_as_string)
        )

        # Error producer lambda function [Dummy]
        producer_lambda = _lambda.Function(
            self,
            "errorProducer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="produceEvents.lambda_handler",
            code=_lambda.Code.from_asset("lambda", exclude=["errorHandler.py"]),
        )

        # Error Handler lambda function + Sends email notification
        error_handler_lambda = _lambda.Function(
            self,
            "errorHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="errorHandler.lambda_handler",
            code=_lambda.Code.from_asset("lambda", exclude=["produceEvents.py"]),
            environment={"SNS_TOPIC_ARN": sns_topic.topic_arn},
        )

        # Creates subscription filter
        logs.SubscriptionFilter(
            self,
            "Subscription",
            log_group=producer_lambda.log_group,
            destination=destinations.LambdaDestination(error_handler_lambda),
            filter_pattern=logs.FilterPattern.any_term("ERROR", "INFO", "CRITICAL"),
        )

        # Grant SNS publish permission to lambda
        sns_topic.grant_publish(error_handler_lambda)
