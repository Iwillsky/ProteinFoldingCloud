import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import time
import os
import sys
import configparser
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

def job_pushresult(strjobid, urlBlobResult):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' opened'.format(DATABASE_ID))

        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' opened'.format(CONTAINER_ID))        

        items = list(container.query_items(        
            query="SELECT * FROM r WHERE r.jobid=@jobid",
            parameters=[
                { "name":"@jobid", "value": strjobid }
            ],               
            enable_cross_partition_query=True,
            max_item_count=1
        ))
        docid = items[0].get("id")
        
        read_item = container.read_item(item=docid, partition_key=strjobid)
        read_item['state'] = 'COMPLETED'
        read_item['resultblobURL'] = urlBlobResult
        response = container.replace_item(item=read_item, body=read_item)

        print("Job result pushed")
        
    except exceptions.CosmosHttpResponseError as e:
        print('\nJob result push caught an error. {0}'.format(e.message))

    finally:
        print("\nJob result push exit")

if __name__ == '__main__':
    job_pushresult(sys.arg[1], sys.arg[2])