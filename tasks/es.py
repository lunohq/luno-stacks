from __future__ import absolute_import

import copy
import logging
import boto3
from elasticsearch.helpers import bulk
from invoke import ctask as task

from es.indices.actions import (
    create_index,
    delete_index,
    get_connection,
    get_indices_to_migrate,
    get_index_name,
    migrate_index,
    swap_aliases,
)
from es.types.reply import ReplyV1

logger = logging.getLogger(__name__)


def get_config(ctx):
    return ctx[ctx.env]


def connection(ctx):
    config = get_config(ctx)
    return get_connection(config.es.host, config.es.region)


def get_dynamo_connection(ctx):
    config = get_config(ctx)
    return boto3.resource('dynamodb', region_name=config.dynamo.region)


def composite(*ids):
    return ':'.join(ids)


def _get_table(table_name, ctx):
    config = get_config(ctx)
    conn = get_dynamo_connection(ctx)
    return conn.Table(getattr(config.dynamo.tables, table_name))


def get_reply_table(ctx):
    return _get_table('reply', ctx)


def get_topic_item_table(ctx):
    return _get_table('topic_item', ctx)


def get_topic_table(ctx):
    return _get_table('topic', ctx)


def scan_all(table, last_evaluated_key=None, **kwargs):
    items = []
    params = copy.deepcopy(kwargs)
    if last_evaluated_key:
        params['ExclusiveStartKey'] = last_evaluated_key

    response = table.scan(**params)
    items.extend(response['Items'])

    last_evaluated_key = response.get('LastEvaluatedKey')
    if last_evaluated_key:
        more = scan_all(
            table,
            last_evaluated_key=last_evaluated_key,
            **kwargs
        )
        items.extend(more)
    return items


@task
def new(ctx, version=None):
    es = connection(ctx)

    params = {'conn': es}
    if version is not None:
        params['version'] = version

    logger.info('creating index...')
    index = create_index(**params)
    logger.info('created index: %s', index._name)
    return index._name


@task
def migrate(ctx):
    es = connection(ctx)

    indices = get_indices_to_migrate(es)
    logger.info('migrating %d indices...', len(indices))
    for index in indices:
        logger.info('...migrating index: %s', index)
        migrate_index(es, index)
    logger.info('migrated indices')


@task
def delete(ctx):
    es = connection(ctx)

    indices = get_indices_to_migrate(es, current_version=-1)
    logger.info('deleting %d indices...', len(indices))
    for index in indices:
        logger.info('...deleting index: %s', index)
        delete_index(es, index)
    logger.info('deleted indices')


def refresh_reply_index(
        ctx,
        es,
        index_name,
        last_evaluated_key=None,
        topic_item_map=None,
        topic_map=None,
    ):
    if topic_item_map is None:
        topic_item_map = {}
        table = get_topic_item_table(ctx)
        items = scan_all(table)
        for item in items:
            c = composite(item['teamId'], item['itemId'])
            topic_item_map[c] = item

    if topic_map is None:
        topic_map = {}
        table = get_topic_table(ctx)
        items = scan_all(table)
        for item in items:
            c = composite(item['teamId'], item['id'])
            topic_map[c] = item

    reply = get_reply_table(ctx)
    kwargs = {}
    if last_evaluated_key:
        kwargs['ExclusiveStartKey'] = last_evaluated_key

    response = reply.scan(**kwargs)
    items = []
    for item in response['Items']:
        item_id = item.pop('id')
        team_id = item['teamId']
        try:
            topic_item = topic_item_map[composite(team_id, item_id)]
        except KeyError:
            print 'error fetching topic item'
            raise

        try:
            topic = topic_map[composite(team_id, topic_item['topicId'])]
        except KeyError:
            print 'error fetching topic'
            raise

        item['titleV2'] = item['title']
        item['topicId'] = topic['id']
        if topic.get('displayName'):
            item['title'] = u'[{}] {}'.format(topic['displayName'], item['title']).strip()
            item['topic'] = topic['displayName']

        item['displayTitle'] = item['title']
        if item.get('keywords'):
            keywords = [k.strip() for k in item['keywords'].strip().split(',')
                        if k.strip()]
            item['title'] = u'{} {}'.format(item['title'], ' '.join(keywords))
            item['keywords'] = keywords

        attachments = item.get('attachments')
        if attachments:
            formatted_attachments = []
            for attachment in attachments:
                formatted = u'<{}|{}>'.format(
                    attachment['file']['permalink'],
                    attachment['file']['name'],
                )
                formatted_attachments.append(formatted)
            item['body'] = u'{}\n---\n{}'.format(
                item['body'],
                u'_Attachments: {}_'.format(
                    ', '.join(formatted_attachments),
                ),
            )

        reply = ReplyV1(
            _routing=team_id,
            _id=item_id,
            _index=index_name,
            **item
        )
        items.append(reply.to_dict(include_meta=True))
    bulk(es, items, chunk_size=500)
    last = response.get('LastEvaluatedKey')
    if last:
        logger.info('fetching next set of replies: %s', last)
        refresh_reply_index(
            ctx,
            es,
            index_name,
            last_evaluated_key=last,
            topic_map=topic_map,
            topic_item_map=topic_item_map,
        )


@task
def refresh(ctx):
    es = connection(ctx)
    old_index = get_index_name(es)
    index = create_index(es, setup_read_alias=False)
    index_name = index._name
    logger.info('Loading data into: %s', index_name)
    refresh_reply_index(ctx, es, index_name)
    swap = raw_input('Swap aliases? (y/n) ')
    if swap != 'y':
        logger.info('Leaving index: %s as primary', old_index)
        return

    logger.info('Swapping alias from: %s to %s', old_index, index_name)
    swap_aliases(
        es,
        old_index_name=old_index,
        new_index_name=index_name,
    )
    remove_index(es, old_index)


@task
def swap(ctx, old_index, new_index):
    es = connection(ctx)
    indices = get_indices_to_migrate(es, current_version=-1)
    for index in [old_index, new_index]:
        if index not in indices:
            raise Exception('Invalid index: {}'.format(index))
    logger.info('Swapping alias from: %s to %s', old_index, new_index)
    swap_aliases(
        es,
        old_index_name=old_index,
        new_index_name=new_index,
    )
    remove_index(es, old_index)


@task
def remove(ctx, index_name):
    es = connection(ctx)
    remove_index(es, index_name)


def remove_index(es, index_name):
    remove = raw_input('Remove old index: {}? (y/n) '.format(index_name))
    if remove != 'y':
        logger.info('Leaving old index: %s', index_name)
        return

    logger.info('Removing old index: %s', index_name)
    delete_index(es, index_name)
