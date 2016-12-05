from awacs.aws import (
    Allow,
    Policy,
    Statement,
)
import awacs.sns
from stacker.blueprints.base import Blueprint
from troposphere import (
    iam,
    sns,
    Output,
    Ref,
)

SLACK_NOTIFICATION_TOPIC = 'SlackNotificationTopic'
NEW_TEAM_TOPIC = 'NewTeamTopic'
NEW_USER_TOPIC = 'NewUserTopic'
ROLE_TOPICS_POLICY = 'RoleTopicsPolicy'


class SNS(Blueprint):

    PARAMETERS = {
        'Role': {
            'type': 'String',
            'description': 'The role that should have access to publish to the SNS topics',
        },
    }

    def topics_policy(self):
        statements = [
            Statement(
                Effect=Allow,
                Action=[
                    awacs.sns.Publish,
                ],
                Resource=[Ref(NEW_USER_TOPIC), Ref(NEW_TEAM_TOPIC)],
            ),
        ]
        return Policy(Statement=statements)

    def create_topics(self):
        t = self.template
        t.add_resource(sns.Topic(NEW_USER_TOPIC))
        t.add_output(Output('NewUserTopic', Value=Ref(NEW_USER_TOPIC)))
        t.add_resource(sns.Topic(NEW_TEAM_TOPIC))
        t.add_output(Output('NewTeamTopic', Value=Ref(NEW_TEAM_TOPIC)))
        t.add_resource(sns.Topic(SLACK_NOTIFICATION_TOPIC))
        t.add_output(Output('SlackNotificationTopic', Value=Ref(SLACK_NOTIFICATION_TOPIC)))

    def create_policy(self):
        ns = self.context.namespace
        t = self.template
        t.add_resource(
            iam.PolicyType(
                ROLE_TOPICS_POLICY,
                PolicyName='{}-topics'.format(ns),
                PolicyDocument=self.topics_policy(),
                Roles=[Ref('Role')],
            ),
        )

    def create_template(self):
        self.create_topics()
        self.create_policy()
