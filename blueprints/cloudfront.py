import os

from awacs.aws import (
    Allow,
    AWSPrincipal,
    Everybody,
    Policy,
    Statement,
)
import awacs.s3
from stacker.blueprints.base import Blueprint
from troposphere import (
    cloudfront as cf,
    iam,
    s3,
    GetAtt,
    Join,
    Output,
    Ref,
)

BUCKET = 'S3Bucket'
BUCKET_POLICY = 'S3BucketPolicy'
ROLE_POLICY = 'S3RolePolicy'
DISTRIBUTION = 'CFDistribution'


class CloudFront(Blueprint):

    LOCAL_PARAMETERS = {
        'BucketName': {
            'type': str,
            'description': 'Name of the bucket to use as an origin',
        },
    }

    PARAMETERS = {
        'Role': {
            'type': 'String',
            'description': 'The role that should have access to write to the s3 bucket',
        },
        'Enabled': {
            'type': 'String',
            'allowed_values': ['true', 'false'],
            'description': 'Boolean for whether or not the distribution is enabled',
        },
    }

    def _role_policy(self):
        bucket_name = self.local_parameters['BucketName']
        statements = [
            Statement(
                Effect=Allow,
                Action=[
                    awacs.s3.ListBucket,
                    awacs.s3.PutObject,
                    awacs.s3.GetObjectVersion,
                ],
                Resource=[
                    awacs.s3.ARN(bucket_name),
                    awacs.s3.ARN(os.path.join(bucket_name, '*')),
                ],
            ),
        ]
        return Policy(Statement=statements)

    def create_policy(self):
        ns = self.context.namespace
        t = self.template
        t.add_resource(
            iam.PolicyType(
                ROLE_POLICY,
                PolicyName='{}-cloudfront'.format(ns),
                PolicyDocument=self._role_policy(),
                Roles=[Ref('Role')],
            ),
        )

    def create_s3_bucket(self):
        t = self.template
        bucket_name = self.local_parameters['BucketName']
        t.add_resource(
            s3.Bucket(
                BUCKET,
                BucketName=bucket_name,
            ),
        )
        t.add_resource(
            s3.BucketPolicy(
                BUCKET_POLICY,
                Bucket=Ref(BUCKET),
                PolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[awacs.s3.GetObject],
                            Resource=[awacs.s3.ARN(os.path.join(bucket_name, '*'))],
                            Principal=AWSPrincipal(Everybody),
                        )
                    ],
                ),
            ),
        )

    def create_distribution(self):
        t = self.template
        t.add_resource(
            cf.Distribution(
                DISTRIBUTION,
                DistributionConfig=cf.DistributionConfig(
                    Origins=[cf.Origin(
                        Id='1',
                        DomainName=GetAtt(BUCKET, 'DomainName'),
                        S3OriginConfig=cf.S3Origin(),
                    )],
                    Enabled=Ref('Enabled'),
                    DefaultCacheBehavior=cf.DefaultCacheBehavior(
                        TargetOriginId='1',
                        ForwardedValues=cf.ForwardedValues(
                            QueryString=False,
                        ),
                        ViewerProtocolPolicy='allow-all',
                    ),
                ),
            )
        )
        t.add_output(
            Output('DomainName', Value=Join('', ['https://', GetAtt(DISTRIBUTION, 'DomainName')]))
        )

    def create_template(self):
        self.create_s3_bucket()
        self.create_policy()
        self.create_distribution()
