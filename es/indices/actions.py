import re

from awses.connection import AWSConnection
from elasticsearch import Elasticsearch
from elasticsearch.helpers import reindex
from elasticsearch_dsl import Index

from . import INDEX_VERSION
from ..analysis import default_search
from ..types.reply import ReplyV1


def get_write_alias():
    return 'luno-bot-write'


def get_read_alias():
    return 'luno-bot-read'


def get_index_name(conn, version=None, minor_version=None, bump_minor=False):
    current_name = get_current_index_name(conn)
    if minor_version is None:
        minor_version = get_minor_version(current_name)
    if bump_minor:
        minor_version += 1
    version = version or INDEX_VERSION
    return 'luno-bot-v{}.{}'.format(version, minor_version)


def get_minor_version(index_name):
    match = re.search('v[0-9\.]+', index_name)
    minor = 0
    if match:
        versions = match.group().split('.')
        if len(versions) == 2:
            minor = int(versions[1])
    return minor


def get_connection(host, region):
    es = Elasticsearch(
        connection_class=AWSConnection,
        region=region,
        host=host,
    )
    return es


def get_current_index_name(conn):
    try:
        indices = conn.cat.indices(get_read_alias(), h='index').strip().split('\n')
    except Exception as e:
        if e.status_code == 404:
            return ''
        raise
    assert len(indices) <= 1, 'Expected only 1 index: {}'.format(indices)
    return indices[0].strip() if len(indices) else ''


def create_index(
        conn,
        version=None,
        minor_version=None,
        setup_write_alias=True,
        setup_read_alias=True,
    ):
    index_name = get_index_name(
        conn,
        version=version,
        minor_version=minor_version,
        bump_minor=minor_version is None,
    )
    index = Index(index_name, using=conn)

    aliases = {}
    if setup_write_alias:
        write_alias = get_write_alias()
        aliases[write_alias] = {}
    if setup_read_alias:
        read_alias = get_read_alias()
        aliases[read_alias] = {}

    if aliases:
        index.aliases(**aliases)

    index.settings(index={'analysis': default_search.get_analysis_definition()})

    # register the doc types
    index.doc_type(ReplyV1)

    index.create()
    return index


def get_indices_to_migrate(conn, current_version=INDEX_VERSION):
    indices = [i.strip() for i in conn.cat.indices(h='index').split(' \n')
               if i.strip()]
    is_old_index = lambda index: (
        len(index) > 3 and
        index.find('v') != -1 and
        not index[index.find('v') + 1:].startswith(str(current_version))
    )
    return [index for index in indices if is_old_index(index)]


def migrate_index(conn, index_name, current_version=INDEX_VERSION):
    new_index = create_index(
        conn,
        version=current_version,
        minor_version=0,
        setup_read_alias=False,
    )
    reindex(conn, source_index=index_name, target_index=new_index._name)
    swap_aliases(
        conn,
        old_index_name=index_name,
        new_index_name=new_index._name,
    )
    delete_index(conn, index_name)
    return new_index


def swap_aliases(conn, old_index_name, new_index_name):
    read_alias = get_read_alias()
    write_alias = get_write_alias()
    conn.indices.update_aliases(body={
        'actions': [
            {'remove': {'index': old_index_name, 'alias': read_alias}},
            {'add': {'index': new_index_name, 'alias': read_alias}},
            {'remove': {'index': old_index_name, 'alias': write_alias}},
        ]
    })


def delete_index(conn, index_name):
    conn.indices.delete(index_name)
