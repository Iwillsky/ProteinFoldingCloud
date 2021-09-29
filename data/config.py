import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://hacktest.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', '7iE999aQxxo6Y3HtZJv46OQzJBlY6E5B3EKVsjzuYsyiwjSAZZWaQxfOgGSXco7bHWlM8tJrxTywBR1uu0X4GQ=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'hackjoblist'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'joblist'),
}