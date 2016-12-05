from awacs.aws import (
    Allow,
    Condition,
    Policy,
    Principal,
    Statement,
    StringEquals,
)
import awacs.firehose
import awacs.logs
import awacs.s3
from awacs import sts
from stacker.blueprints.base import Blueprint
from troposphere import (
    iam,
    logs,
    s3,
    Join,
    Output,
    Ref,
)

S3_BUCKET = 'S3Bucket'
FIREHOSE_WRITE_POLICY = 'FirehoseWriteAccess'
LOGS_POLICY = 'LogsPolicy'
S3_WRITE_POLICY = 'S3WriteAccess'
LOGS_WRITE_POLICY = 'LogsWriteAccess'
FIREHOSE_ROLE = 'FirehoseRole'
LOG_GROUP = 'LogGroup'


def logs_policy():
    statements = [
        Statement(
            Effect=Allow,
            Action=[
                awacs.logs.CreateLogStream,
            ],
            Resource=['*'],
        ),
    ]
    return Policy(Statement=statements)


def firehose_write_policy():
    statements = [
        Statement(
            Effect=Allow,
            Action=[
                awacs.firehose.CreateDeliveryStream,
                awacs.firehose.DeleteDeliveryStream,
                awacs.firehose.DescribeDeliveryStream,
                awacs.firehose.PutRecord,
                awacs.firehose.PutRecordBatch,
            ],
            Resource=['*'],
        ),
    ]
    return Policy(Statement=statements)


def logs_write_policy():
    statements = [
        Statement(
            Effect=Allow,
            Action=[
                awacs.logs.PutLogEvents,
            ],
            Resource=['*'],
        ),
    ]
    return Policy(Statement=statements)


def s3_write_policy(bucket):

    def s3_arn(bucket):
        return Join(':', ['arn:aws:s3::', bucket])

    statements = [
        Statement(
            Effect=Allow,
            Action=[
                awacs.s3.AbortMultipartUpload,
                awacs.s3.GetBucketLocation,
                awacs.s3.GetObject,
                awacs.s3.ListBucket,
                awacs.s3.ListBucketMultipartUploads,
                awacs.s3.PutObject,
            ],
            Resource=[
                s3_arn(bucket),
                s3_arn(Join('/', [bucket, '*'])),
            ],
        ),
    ]
    return Policy(Statement=statements)


class BotFirehose(Blueprint):

    PARAMETERS = {
        'Role': {
            'type': 'String',
            'description': 'The role that should have access to write to firehose',
        },
        'BucketName': {
            'type': 'String',
            'description': 'Name for the S3 Bucket',
        },
    }

    def generate_iam_policies(self):
        ns = self.context.namespace
        s3_policy = iam.Policy(
            S3_WRITE_POLICY,
            PolicyName='{}-s3-write'.format(ns),
            PolicyDocument=s3_write_policy(Ref('BucketName')),
        )
        logs_policy = iam.Policy(
            LOGS_WRITE_POLICY,
            PolicyName='{}-logs-write'.format(ns),
            PolicyDocument=logs_write_policy(),
        )
        return [s3_policy, logs_policy]

    def create_role(self):
        t = self.template

        statements = [
            Statement(
                Principal=Principal('Service', ['firehose.amazonaws.com']),
                Effect=Allow,
                Action=[sts.AssumeRole],
                Condition=Condition(
                    StringEquals('sts:ExternalId', Ref('AWS::AccountId')),
                ),
            ),
        ]
        firehose_role_policy = Policy(Statement=statements)
        t.add_resource(
            iam.Role(
                FIREHOSE_ROLE,
                AssumeRolePolicyDocument=firehose_role_policy,
                Path='/',
                Policies=self.generate_iam_policies(),
            ),
        )
        t.add_output(Output('Role', Value=Ref(FIREHOSE_ROLE)))

    def create_bucket(self):
        t = self.template
        t.add_resource(
            s3.Bucket(
                S3_BUCKET,
                BucketName=Ref('BucketName'),
            )
        )
        t.add_output(Output('Bucket', Value=Ref(S3_BUCKET)))

    def create_policy(self):
        ns = self.context.namespace
        t = self.template
        t.add_resource(
            iam.PolicyType(
                FIREHOSE_WRITE_POLICY,
                PolicyName='{}-bot-firehose'.format(ns),
                PolicyDocument=firehose_write_policy(),
                Roles=[Ref('Role')],
            ),
        )
        t.add_resource(
            iam.PolicyType(
                LOGS_POLICY,
                PolicyName='{}-bot-logs'.format(ns),
                PolicyDocument=logs_policy(),
                Roles=[Ref('Role')],
            ),
        )

    def create_log_group(self):
        t = self.template
        t.add_resource(logs.LogGroup(LOG_GROUP))
        t.add_output(Output('LogGroup', Value=Ref(LOG_GROUP)))

    def create_template(self):
        self.create_policy()
        self.create_bucket()
        self.create_role()
        self.create_log_group()
