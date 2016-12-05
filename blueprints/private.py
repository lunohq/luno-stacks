import os

import awacs.s3
from awacs.aws import (
    Allow,
    Policy,
    Statement,
)
from stacker.blueprints.base import Blueprint
from troposphere import (
    Ref,
    iam,
    s3,
)

BUCKET = 'S3Bucket'
BUCKET_POLICY = 'ReadPolicy'


class Bucket(Blueprint):

    LOCAL_PARAMETERS = {
        'BucketName': {
            'type': str,
            'description': 'The name to use for bucket',
        },
    }

    PARAMETERS = {
        'Roles': {
            'type': 'CommaDelimitedList',
            'description': (
                'The roles that should have access to read and write from the '
                'bucket'
            ),
            'default': '',
        },
    }

    def create_template(self):
        bucket_name = self.local_parameters['BucketName']
        self.template.add_resource(
            s3.Bucket(
                BUCKET,
                BucketName=bucket_name,
            ),
        )
        statements = [
            Statement(
                Effect=Allow,
                Action=[
                    awacs.s3.GetObject,
                    awacs.s3.ListBucket,
                    awacs.s3.PutObject,
                ],
                Resource=[
                    awacs.s3.ARN(bucket_name),
                    awacs.s3.ARN(os.path.join(bucket_name, '*')),
                ],
            ),
        ]
        self.template.add_resource(
            iam.PolicyType(
                BUCKET_POLICY,
                PolicyName='PrivateBucketPolicy',
                PolicyDocument=Policy(
                    Statement=statements,
                ),
                Roles=Ref('Roles'),
            ),
        )
