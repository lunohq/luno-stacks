"""DynamoDB schema"""
import awacs.dynamodb
from awacs.aws import (
    Allow,
    Policy,
    Statement,
)
from stacker.blueprints.base import Blueprint
from troposphere import (
    dynamodb2 as dynamodb,
    iam,
    Join,
    Ref,
    Retain,
)


def create_team_table(t):
    table = dynamodb.Table(
        'Team',
        KeySchema=[dynamodb.KeySchema(
            AttributeName='id',
            KeyType='HASH',
        )],
        TableName=Ref('TeamTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('TeamTableReadCapacity'),
            WriteCapacityUnits=Ref('TeamTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_admin_token_table(t):
    table = dynamodb.Table(
        'AdminToken',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='HASH',
            ),
        ],
        TableName=Ref('AdminTokenTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('AdminTokenTableReadCapacity'),
            WriteCapacityUnits=Ref('AdminTokenTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_token_table(t):
    table = dynamodb.Table(
        'Token',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='userId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('TokenTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('TokenTableReadCapacity'),
            WriteCapacityUnits=Ref('TokenTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='userId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_user_table(t):
    table = dynamodb.Table(
        'User',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='HASH',
            ),
        ],
        TableName=Ref('UserTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('UserTableReadCapacity'),
            WriteCapacityUnits=Ref('UserTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_bot_table(t):
    table = dynamodb.Table(
        'Bot',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('BotTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('BotTableReadCapacity'),
            WriteCapacityUnits=Ref('BotTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_answer_table(t):
    table = dynamodb.Table(
        'Answer',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='botId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('AnswerTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('AnswerTableReadCapacity'),
            WriteCapacityUnits=Ref('AnswerTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='botId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='created',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
        ],
        LocalSecondaryIndexes=[
            dynamodb.LocalSecondaryIndex(
                IndexName='AnswerBotIdCreated',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='botId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='created',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='ALL'),
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='AnswerTeamIdCreated',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='created',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='KEYS_ONLY'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=Ref('AnswerTeamIdCreatedIndexReadCapacity'),
                    WriteCapacityUnits=Ref('AnswerTeamIdCreatedIndexWriteCapacity'),
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_reply_table(t):
    table = dynamodb.Table(
        'Reply',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('ReplyTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=1,
            WriteCapacityUnits=1,
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='created',
                AttributeType='S',
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdCreated',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='created',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='KEYS_ONLY'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=1,
                    WriteCapacityUnits=1,
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_thread_table(t):
    table = dynamodb.Table(
        'Thread',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='botIdChannelIdUserId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('ThreadTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('ThreadTableReadCapacity'),
            WriteCapacityUnits=Ref('ThreadTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='botIdChannelIdUserId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='status',
                AttributeType='N',
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='ThreadBotIdChannelIdUserIdStatus',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='botIdChannelIdUserId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='status',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='ALL'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=Ref('ThreadBotIdChannelIdUserIdStatusIndexReadCapacity'),
                    WriteCapacityUnits=Ref('ThreadBotIdChannelIdUserIdStatusIndexWriteCapacity'),
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_thread_log_table(t, params):
    table = dynamodb.Table(
        'ThreadLog',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='threadId',
                KeyType='RANGE',
            ),
        ],
        TableName=params['ThreadLogTableName'],
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=params['ThreadLogTableReadCapacity'],
            WriteCapacityUnits=params['ThreadLogTableWriteCapacity'],
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='threadId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='created',
                AttributeType='S',
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdCreated',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='created',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='ALL'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=params[
                        'ThreadLogTableTeamIdCreatedIndexReadCapacity'
                    ],
                    WriteCapacityUnits=params[
                        'ThreadLogTableTeamIdCreatedIndexWriteCapacity'
                    ],
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_thread_event_table(t):
    table = dynamodb.Table(
        'ThreadEvent',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='threadId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='created',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('ThreadEventTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('ThreadEventTableReadCapacity'),
            WriteCapacityUnits=Ref('ThreadEventTableWriteCapacity'),
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='threadId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='created',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='botIdChannelIdMessageId',
                AttributeType='S',
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='ThreadEventBotIdChannelIdMessageId',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='botIdChannelIdMessageId',
                        KeyType='HASH',
                    ),
                ],
                Projection=dynamodb.Projection(
                    NonKeyAttributes=['userId'],
                    ProjectionType='INCLUDE',
                ),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=Ref('ThreadEventBotIdChannelIdMessageIdIndexReadCapacity'),
                    WriteCapacityUnits=Ref('ThreadEventBotIdChannelIdMessageIdIndexWriteCapacity'),
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_topic_table(t):
    table = dynamodb.Table(
        'Topic',
        TableName=Ref('TopicTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('TopicTableReadCapacity'),
            WriteCapacityUnits=Ref('TopicTableWriteCapacity'),
        ),
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='name',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='isDefault',
                AttributeType='N',
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdNameIndex',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='name',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='KEYS_ONLY'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=1,
                    WriteCapacityUnits=1,
                ),
            ),
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdNameIndexV2',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='name',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(
                    NonKeyAttributes=['displayName'],
                    ProjectionType='INCLUDE',
                ),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=1,
                    WriteCapacityUnits=1,
                ),
            ),
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdIsDefaultIndex',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='isDefault',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='KEYS_ONLY'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=1,
                    WriteCapacityUnits=1,
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_topic_name_table(t):
    table = dynamodb.Table(
        'TopicName',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='name',
                KeyType='RANGE',
            ),
        ],
        TableName=Ref('TopicNameTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=1,
            WriteCapacityUnits=1,
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='name',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_topic_item_table(t):
    table = dynamodb.Table(
        'TopicItem',
        TableName=Ref('TopicItemTableName'),
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=Ref('TopicItemReadCapacity'),
            WriteCapacityUnits=Ref('TopicItemWriteCapacity'),
        ),
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamIdTopicId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='itemId',
                KeyType='RANGE',
            ),
        ],
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='teamIdTopicId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='itemId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='created',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
        ],
        GlobalSecondaryIndexes=[
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdTopicIdCreatedIndex',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamIdTopicId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='created',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(ProjectionType='KEYS_ONLY'),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=1,
                    WriteCapacityUnits=1,
                ),
            ),
            dynamodb.GlobalSecondaryIndex(
                IndexName='TeamIdItemIdIndex',
                KeySchema=[
                    dynamodb.KeySchema(
                        AttributeName='teamId',
                        KeyType='HASH',
                    ),
                    dynamodb.KeySchema(
                        AttributeName='itemId',
                        KeyType='RANGE',
                    ),
                ],
                Projection=dynamodb.Projection(
                    NonKeyAttributes=['topicId'],
                    ProjectionType='INCLUDE',
                ),
                ProvisionedThroughput=dynamodb.ProvisionedThroughput(
                    ReadCapacityUnits=1,
                    WriteCapacityUnits=1,
                ),
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_file_table(t, params):
    table = dynamodb.Table(
        'File',
        KeySchema=[
            dynamodb.KeySchema(
                AttributeName='teamId',
                KeyType='HASH',
            ),
            dynamodb.KeySchema(
                AttributeName='id',
                KeyType='RANGE',
            ),
        ],
        TableName=params['FileTableName'],
        DeletionPolicy=Retain,
        ProvisionedThroughput=dynamodb.ProvisionedThroughput(
            ReadCapacityUnits=params['FileTableReadCapacity'],
            WriteCapacityUnits=params['FileTableWriteCapacity'],
        ),
        AttributeDefinitions=[
            dynamodb.AttributeDefinition(
                AttributeName='teamId',
                AttributeType='S',
            ),
            dynamodb.AttributeDefinition(
                AttributeName='id',
                AttributeType='S',
            ),
        ],
    )
    t.add_resource(table)
    return table


def create_policy(t, tables):
    policy_name = 'DynamodbPolicy'

    table_resources = [get_dynamo_arn(table) for table in tables]
    indices_resources = [get_dynamo_arn(table, '*') for table in tables]

    statements = [
        Statement(
            Effect=Allow,
            Action=[
                awacs.dynamodb.BatchGetItem,
                awacs.dynamodb.BatchWriteItem,
                awacs.dynamodb.DeleteItem,
                awacs.dynamodb.GetItem,
                awacs.dynamodb.PutItem,
                awacs.dynamodb.Query,
                awacs.dynamodb.Scan,
                awacs.dynamodb.UpdateItem,
            ],
            Resource=table_resources + indices_resources,
        ),
    ]
    t.add_resource(
        iam.PolicyType(
            policy_name,
            PolicyName=policy_name,
            PolicyDocument=Policy(Statement=statements),
            Roles=Ref('Roles'),
        )
    )


def get_dynamo_arn(table, extra_path=None):
    path = ['table', Ref(table)]
    if extra_path:
        path.append(extra_path)

    return Join(':', [
        'arn',
        'aws',
        awacs.dynamodb.prefix,
        Ref('AWS::Region'),
        Ref('AWS::AccountId'),
        Join('/', path),
    ])


class Schema(Blueprint):

    LOCAL_PARAMETERS = {
        'ThreadLogTableName': {
            'type': str,
        },
        'ThreadLogTableReadCapacity': {
            'type': int,
            'default': 1,
        },
        'ThreadLogTableWriteCapacity': {
            'type': int,
            'default': 1,
        },
        'ThreadLogTableTeamIdCreatedIndexReadCapacity': {
            'type': int,
            'default': 1,
        },
        'ThreadLogTableTeamIdCreatedIndexWriteCapacity': {
            'type': int,
            'default': 1,
        },
        'FileTableName': {
            'type': str,
        },
        'FileTableReadCapacity': {
            'type': int,
            'default': 1,
        },
        'FileTableWriteCapacity': {
            'type': int,
            'default': 1,
        },
    }

    PARAMETERS = {
        'Roles': {
            'type': 'CommaDelimitedList',
            'description': 'The roles that should have access to write and query the tables',
        },
        'TeamTableName': {
            'type': 'String',
            'description': 'The name of the team table',
        },
        'TeamTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the team table',
            'default': '1',
        },
        'TeamTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the team table',
            'default': '1',
        },
        'UserTableName': {
            'type': 'String',
            'description': 'The name of the user table',
        },
        'UserTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the user table',
            'default': '1',
        },
        'UserTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the user table',
            'default': '1',
        },
        'BotTableName': {
            'type': 'String',
            'description': 'The name of the bot table',
        },
        'BotTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the bot table',
            'default': '1',
        },
        'BotTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the bot table',
            'default': '1',
        },
        'AnswerTableName': {
            'type': 'String',
            'description': 'The name of the answer table',
        },
        'AnswerTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the answer table',
            'default': '1',
        },
        'AnswerTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the answer table',
            'default': '1',
        },
        'AnswerTeamIdCreatedIndexReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the AnswerTeamIdCreated index',
            'default': '1',
        },
        'AnswerTeamIdCreatedIndexWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the AnswerTeamIdCreated index',
            'default': '1',
        },
        'ReplyTableName': {
            'type': 'String',
            'description': 'The name of the reply table',
        },
        'ThreadTableName': {
            'type': 'String',
            'description': 'The name of the thread table',
        },
        'ThreadTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the thread table',
            'default': '1',
        },
        'ThreadTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the thread table',
            'default': '1',
        },
        'ThreadBotIdChannelIdUserIdStatusIndexReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity from the ThreadBotIdChannelIdUserIdStatus index',
            'default': '1',
        },
        'ThreadBotIdChannelIdUserIdStatusIndexWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity from the ThreadBotIdChannelIdUserIdStatus index',
            'default': '1',
        },
        'ThreadEventTableName': {
            'type': 'String',
            'description': 'The name of the thread events table',
        },
        'ThreadEventTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the thread event table',
            'default': '1',
        },
        'ThreadEventTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the thread event table',
            'default': '1',
        },
        'ThreadEventBotIdChannelIdMessageIdIndexReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the ThreadEventBotIdChannelIdMessageId index',
            'default': '1',
        },
        'ThreadEventBotIdChannelIdMessageIdIndexWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the ThreadEventBotIdChannelIdMessageId index',
            'default': '1',
        },
        'TokenTableName': {
            'type': 'String',
            'description': 'The name of the token table',
        },
        'TokenTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the token table',
            'default': '1',
        },
        'TokenTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the token table',
            'default': '1',
        },
        'AdminTokenTableName': {
            'type': 'String',
            'description': 'The name of the admin token table',
        },
        'AdminTokenTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity for the admin token table',
            'default': '1',
        },
        'AdminTokenTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity for the admin token table',
            'default': '1',
        },
        'TopicNameTableName': {
            'type': 'String',
            'description': 'The name of the topic name table',
        },
        'TopicTableName': {
            'type': 'String',
            'description': 'The name of the topic table',
        },
        'TopicTableReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity',
            'default': '1',
        },
        'TopicTableWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity',
            'default': '1',
        },
        'TopicItemTableName': {
            'type': 'String',
            'description': 'The name of the topic answers table',
        },
        'TopicItemReadCapacity': {
            'type': 'Number',
            'description': 'Read capacity',
            'default': '1',
        },
        'TopicItemWriteCapacity': {
            'type': 'Number',
            'description': 'Write capacity',
            'default': '1',
        },
    }

    def create_template(self):
        t = self.template
        team_table = create_team_table(t)
        user_table = create_user_table(t)
        bot_table = create_bot_table(t)
        answer_table = create_answer_table(t)
        token_table = create_token_table(t)
        thread_table = create_thread_table(t)
        thread_event_table = create_thread_event_table(t)
        admin_token_table = create_admin_token_table(t)
        topic_table = create_topic_table(t)
        topic_name_table = create_topic_name_table(t)
        topic_item_table = create_topic_item_table(t)
        reply_table = create_reply_table(t)
        thread_log_table = create_thread_log_table(t, self.local_parameters)
        file_table = create_file_table(t, self.local_parameters)

        create_policy(t, [
            team_table,
            user_table,
            bot_table,
            answer_table,
            token_table,
            thread_table,
            thread_event_table,
            admin_token_table,
            topic_table,
            topic_name_table,
            topic_item_table,
            reply_table,
            thread_log_table,
            file_table,
        ])
