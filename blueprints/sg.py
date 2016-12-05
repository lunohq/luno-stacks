from stacker.blueprints.base import Blueprint
from troposphere import (
    ec2,
    Ref,
)


class SG(Blueprint):

    PARAMETERS = {
        'RedisSecurityGroup': {
            'type': 'AWS::EC2::SecurityGroup::Id',
            'description': 'Security group for the redis database',
        },
        'MinionSecurityGroup': {
            'type': 'AWS::EC2::SecurityGroup::Id',
            'description': 'Security group for the minions running the API service.',
        },
    }

    def create_security_groups(self):
        self.template.add_resource(
            ec2.SecurityGroupIngress(
                'EmpireMinionRedisAccess',
                IpProtocol='TCP',
                FromPort=6379,
                ToPort=6379,
                SourceSecurityGroupId=Ref('MinionSecurityGroup'),
                GroupId=Ref('RedisSecurityGroup'),
            ),
        )

    def create_template(self):
        self.create_security_groups()
