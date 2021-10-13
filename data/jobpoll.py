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

def job_poll():

    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        db = client.get_database_client(DATABASE_ID)
        #print('Database with id \'{0}\' opened'.format(DATABASE_ID))

        container = db.get_container_client(CONTAINER_ID)
        #print('Container with id \'{0}\' opened'.format(CONTAINER_ID))        
                    
        items = list(container.query_items(        
            query="SELECT * FROM r WHERE r.state=@jobstate",
            parameters=[
                { "name":"@jobstate", "value": "WAIT" }
            ],               
            enable_cross_partition_query=True,
            max_item_count=1
        ))
        #os.environ['PROTEIN_POLL_ARRIVING']='1'
        #os.environ['PROTEIN_POLL_SEQSTR']=items[0].get("inputfilestring")
        #os.environ['PROTEIN_POLL_DOCID']=items[0].get("id")
        #os.environ['PROTEIN_POLL_CURJOBID']=items[0].get("jobid")
        #os.environ['PROTEIN_POLL_INPUTURL']=items[0].get("inputblobURL")
        #os.chdir("")
        cf = configparser.ConfigParser()
        cf.add_section("jobpoll")
        cf.set("jobpoll", "arriving", "1")
        cf.set("jobpoll", "seqstr", items[0].get("inputfilestring"))
        cf.set("jobpoll", "curjobid", items[0].get("jobid"))
        with open("hackjob.ini","w+") as f:
            cf.write(f)

        #print(items[0].get("inputblobURL"))
        
    except exceptions.CosmosHttpResponseError as e:
        print('\nJob polling caught an error. {0}'.format(e.message))

    finally:
        print("\nPoll exit")

if __name__ == '__main__':
    job_poll()       
    
    #job_tag(sys.arg[1])
    #job_tag(os.environ['PROTEIN_POLL_DOCID'], os.environ['PROTEIN_POLL_CURJOBID'])

    #job_refreshstatus(os.environ['PROTEIN_POLL_CURJOBID'], "Status testing string")
    #job_pushresult()
