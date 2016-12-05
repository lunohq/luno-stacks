from stacker.blueprints.base import Blueprint
from troposphere import Ref
from troposphere import ec2


class SlackTTT(Blueprint):

    PARAMETERS = {
        'RDSSecurityGroup': {
            'type': 'AWS::EC2::SecurityGroup::Id',
            'description': 'Security group for the API database.',
        },
        'MinionSecurityGroup': {
            'type': 'AWS::EC2::SecurityGroup::Id',
            'description': 'Security group for the minions running the API service.',
        },
    }

    def create_security_groups(self):
        # Add rules to access RDS and Redis databases from the empire minions
        # that will run the API
        self.template.add_resource(
            ec2.SecurityGroupIngress(
                'EmpireMinionDatabaseAccess',
                IpProtocol='TCP',
                FromPort=5432,
                ToPort=5432,
                SourceSecurityGroupId=Ref('MinionSecurityGroup'),
                GroupId=Ref('RDSSecurityGroup'),
            ),
        )

    def create_template(self):
        self.create_security_groups()
