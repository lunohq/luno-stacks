from elasticsearch_dsl import (
    DocType,
    MetaField,
    String,
)

from ..analysis import (
    luno_english,
    raw_analyzer,
    shingle_analyzer,
)


class ReplyV1(DocType):
    title = String(analyzer=luno_english)
    titleV2 = String(
        analyzer=luno_english,
        fields={
            'raw': String(
                analyzer=raw_analyzer,
            ),
            'shingles': String(
                analyzer=shingle_analyzer,
            ),
        },
    )
    body = String(
        analyzer=luno_english,
        fields={
            'shingles': String(
                analyzer=shingle_analyzer,
            ),
        },
    )
    keywords = String(
        analyzer=luno_english,
        fields={
            'raw': String(
                analyzer=raw_analyzer,
            ),
            'shingles': String(
                analyzer=shingle_analyzer,
            ),
        },
    )
    topic = String(
        analyzer=luno_english,
        fields={
            'raw': String(
                analyzer=raw_analyzer,
            ),
            'shingles': String(
                analyzer=shingle_analyzer,
            ),
        },
    )
    topicId = String(index='not_analyzed')
    teamId = String(index='not_analyzed')

    class Meta:
        doc_type = 'reply'
        all = MetaField(enabled=False)
        dynamic = MetaField('false')
        routing = MetaField(required=True)
