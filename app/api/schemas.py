EQUIDISTANT_FIELDS_SCHEMA = {
    'type': 'object',
    'properties': {
        'geometry': {
            'type': 'object',
        },
        'distance': {
            'type': 'number',
        },
        'crop': {
            'type': 'string',
        },
    },
    'required': ['geometry', 'distance'],
}

STATS_BY_REGION_SCHEMA = {
    'type': 'object',
    'properties': {
        'region': {
            'type': 'string',
            'pattern': '^([A-Z]{2}-(?:\\d|[A-Z]){2,3})$',  # ISO 3166-2
        },
    },
    'required': ['region'],
}
