#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, request, render_template
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from azure.cosmos import CosmosClient
import os
import uuid
import hashlib

app = Flask(__name__, static_url_path = "/static", static_folder = "static")

url = os.environ.get('ACCOUNT_URI', 'https://hacktest.documents.azure.com:443/')
key = os.environ.get('ACCOUNT_KEY', '')
client = CosmosClient(url, credential=key)
database_name = 'hackjoblist'
database = client.get_database_client(database_name)
container_name = 'joblist'
container = database.get_container_client(container_name)

# Intentionally left blank to not make this public
storage_account_name = os.environ.get('STORAGE_ACCOUNT_NAME', 'mshack2021storage')
storage_account_key = os.environ.get('STORAGE_ACCOUNT_KEY', '')
storage_connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net".format(storage_account_name, storage_account_key)

blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

# root endpoint
@app.route("/", methods=["GET", "POST"])
def upload_file():
    # handle post
    if request.method == 'POST':
        # keep list of sequences for upsert and display
        amino_sequences = []
        max_lines = 50
        line_count = 0
        # read file line by line and append each found sequence to list
        f = request.files['file_name']
        line = f.readline().decode("utf-8").strip()

        storage_container_name = str(uuid.uuid4())
        container_client = blob_service_client.create_container(storage_container_name)
        file_upload_name = str(uuid.uuid4()) + ".txt"

        while line:
            line_count += 1
            if line_count >= max_lines:
                break
            if line[0] == '>':
                amino_sequences.append({"title": line[1:]})
            else:
                count = len(amino_sequences) 
                if count:
                    sequence = amino_sequences[count-1]
                    if not sequence.get('value'):
                        sequence['value'] = line
                    else:
                        sequence['value'] += line
            line = f.readline().decode("utf-8").strip()

        # Instantiate a new BlobClient to interact with the blob
        blob_client = blob_service_client.get_blob_client(container=storage_container_name, blob=file_upload_name)

        print("\nUploading to Azure Storage as blob:\n\t" + file_upload_name)
        blob_client.upload_blob(f.read())
        print("\nListing blobs...")

        # List the blobs in the container
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)

        # get the cursor positioned at end
        f.seek(0, os.SEEK_END)
        # this will be equivalent to size of file
        size = f.tell()
        f.close()
        # keep list of jobids for display
        folding_jobids = []
        # upsert found sequences to db
        for seq in amino_sequences:
            jobid = str(uuid.uuid4())
            folding_jobids.append(jobid)
            container.upsert_item({
                'jobid': jobid,
                'state': 'WAIT',
                'statusinfo': '',
                'inputfilestring': seq.get('value'),
                'name': seq.get('title'),
                'resultfileURL': '',
                }
            )
        # get latest list from db for display
        foldingjobs = list(container.query_items(
                query='SELECT * FROM r',
                enable_cross_partition_query=True))
        foldingjobs.reverse()
        return render_template(
            "upload-file.html",
            msg="Uploaded: {} bytes".format(size),
            folding_jobs=foldingjobs,
            jobs=foldingjobs,
            len=len(foldingjobs),
            title='Rosetta Hack 2021')
        
    foldingjobs = list(container.query_items(
                query='SELECT * FROM r',
                enable_cross_partition_query=True))
    foldingjobs.reverse()
    return render_template(
        "upload-file.html", 
        msg="Please choose a file with amino acid (protein) sequences according to FASTA file format.",
        folding_jobs=foldingjobs,
        jobs=foldingjobs,
        len=len(foldingjobs),
        title='Rosetta Hack 2021')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True) 
