"""AWS Elasticsearch Service.

Configures our Elasticsearch resources.

"""
import awacs.es
from awacs.aws import (
    Allow,
    Policy,
    Statement,
)
from stacker.blueprints.base import Blueprint
from troposphere import (
    elasticsearch,
    iam,
    route53,
    And,
    Condition,
    Equals,
    GetAtt,
    Not,
    Join,
    Output,
    Ref,
)

DNS_RECORD = 'ESDomainDNSRecord'


def create_domain(t):
    domain = elasticsearch.ElasticsearchDomain('Domain')
    t.add_resource(domain)
    t.add_output(Output('DomainArn', Value=GetAtt('Domain', 'DomainArn')))
    t.add_output(Output('DomainEndpoint', Value=GetAtt('Domain', 'DomainEndpoint')))
    return domain


def create_policy(t, domain):
    policy_name = 'ESDomainReadAccess'

    statements = [
        Statement(
            Effect=Allow,
            Action=[
                awacs.es.Action('HttpGet'),
                awacs.es.Action('HttpHead'),
                awacs.es.Action('HttpPost'),
                awacs.es.Action('HttpDelete'),
            ],
            Resource=[Join('/', [GetAtt('Domain', 'DomainArn'), '*'])],
        ),
    ]
    t.add_resource(
        iam.PolicyType(
            policy_name,
            PolicyName=policy_name,
            PolicyDocument=Policy(Statement=statements),
            Roles=[Ref('Role')],
        ),
    )


class Elasticsearch(Blueprint):

    PARAMETERS = {
        'Role': {
            'type': 'String',
            'description': 'The role that should have access to query the ES domain',
        },
        'InternalZoneId': {
            'type': 'String',
            'default': '',
            'description': 'Internal zone Id, if you have one.'
        },
        'InternalZoneName': {
            'type': 'String',
            'default': '',
            'description': 'Internal zone name, if you have one.'
        },
        'InternalHostname': {
            'type': 'String',
            'default': '',
            'description': 'Internal domain name, if you have one.'
        },
    }

    def create_conditions(self):
        t = self.template
        t.add_condition(
            'HasInternalZone',
            Not(Equals(Ref('InternalZoneId'), '')))
        t.add_condition(
            'HasInternalZoneName',
            Not(Equals(Ref('InternalZoneName'), '')))
        t.add_condition(
            'HasInternalHostname',
            Not(Equals(Ref('InternalHostname'), '')))
        t.add_condition(
            'CreateInternalHostname',
            And(Condition('HasInternalZone'),
                Condition('HasInternalZoneName'),
                Condition('HasInternalHostname')))

    def create_dns_records(self):
        t = self.template
        t.add_resource(
            route53.RecordSetType(
                DNS_RECORD,
                HostedZoneId=Ref('InternalZoneId'),
                Comment='ES Domain CNAME Record',
                Name=Join('.', [Ref('InternalHostname'), Ref('InternalZoneName')]),
                Type='CNAME',
                TTL='120',
                ResourceRecords=[GetAtt('Domain', 'DomainEndpoint')],
                Condition='CreateInternalHostname',
            )
        )
        t.add_output(Output('CNAME', Condition='CreateInternalHostname', Value=Ref(DNS_RECORD)))

    def create_template(self):
        t = self.template
        self.create_conditions()
        domain = create_domain(t)
        create_policy(t, domain)
        self.create_dns_records()
