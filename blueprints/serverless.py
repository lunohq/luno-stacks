"""Blueprint to configure access to Serverless resources."""
import awacs.awslambda
from awacs.aws import (
    Allow,
    Everybody,
    Policy,
    Statement,
)
from stacker.blueprints.base import Blueprint
from troposphere import (
    iam,
    Ref,
)


class Serverless(Blueprint):

    PARAMETERS = {
        'Role': {
            'type': 'String',
            'description': 'The role that should have access to invoke serverless resources',
        },
    }

    def create_policy(self):
        t = self.template
        ns = self.context.namespace
        policy_name = 'ServerlessPolicy'
        statements = [
            Statement(
                Effect=Allow,
                Action=[awacs.awslambda.InvokeFunction],
                Resource=[Everybody],
            ),
        ]
        t.add_resource(
            iam.PolicyType(
                policy_name,
                PolicyName='{}-{}'.format(ns, policy_name),
                PolicyDocument=Policy(Statement=statements),
                Roles=[Ref('Role')],
            )
        )

    def create_template(self):
        self.create_policy()
