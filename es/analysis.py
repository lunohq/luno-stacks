from elasticsearch_dsl import (
    analyzer,
    token_filter,
)

STOPWORDS = (
    'a able about across after all almost also am among an and '
    'any are as at be because been but by can cannot could dear '
    'did do does either else ever every for from get got had has '
    'have he her hers him his how however i if in into is its '
    'just least let like likely may me might most must my '
    'neither no nor not of off often on only or other our own '
    'rather said say says she should since so some than that the '
    'their them then there these they this tis to too twas us '
    'wants was we were what when where which while who whom why '
    'will with would yet you your whats wheres u ur'.split()
)

default_search = analyzer(
    'default_search',
    tokenizer='whitespace',
    filter=['standard', 'lowercase'],
)

luno_english = analyzer(
    'luno_english',
    type='english',
    stopwords=STOPWORDS,
)

raw_analyzer = analyzer(
    'raw_analyzer',
    tokenizer='keyword',
    filter=['standard', 'lowercase'],
)

english_stemmer = token_filter(
    'english_stemmer',
    type='stemmer',
    language='english',
)

english_possessive_stemmer = token_filter(
    'english_possessive_stemmer',
    type='stemmer',
    language='possessive_english',
)

shingle_filter = token_filter(
    'shingle_filter',
    type='shingle',
    min_shingle_size=2,
    max_shingle_size=4,
    output_unigrams=False,
    output_unigrams_if_no_shingles=False,
)

shingle_analyzer = analyzer(
    'shingle_analyzer',
    tokenizer='standard',
    filter=[
        'standard',
        english_possessive_stemmer,
        'lowercase',
        english_stemmer,
        shingle_filter,
    ],
)
