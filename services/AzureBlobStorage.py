import os
import uuid
import json
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

from models.webhook_model import WebhookModel

# Load app settings
with open("local.settings.json", "r") as settings_file:
    app_settings = json.load(settings_file)

# Initialize the BlobServiceClient
connection_string = os.getenv("WEBHOOK_STORAGE")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

container_name = os.getenv("WIKI_HTML_CONTAINER_NAME")


async def delete_blob(data: WebhookModel) -> None:
    """
    Deletes a blob from the container.

    :param data: The WebhookModel containing project and wiki information.
    """
    # Generate the blob name
    blob_name = f"{data.projectName} - {data.wikiSlug}.html"

    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)

    # Delete the blob if it exists
    try:
        blob_client = container_client.get_blob_client(blob_name)
        await blob_client.delete_blob()
    except Exception as e:
        pass  # Blob likely doesn't exist
    

async def upload_string_and_generate_sas(content: str,data: WebhookModel) -> str:
    """
    Uploads a string to a blob and generates a SAS URL for the blob.

    :param content: The string content to upload.
    :return: SAS URL for the uploaded blob.
    """
    # Generate a unique blob name
    blob_name = f"{data.projectName} - {data.wikiSlug}.html"

   

    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure the container exists
    try:
        await container_client.create_container()
    except Exception:
        pass  # Container likely already exists

    # Upload the string content to the blob
    blob_client = container_client.get_blob_client(blob_name)
    await blob_client.upload_blob(content, overwrite=True)

    # Generate a SAS token for the blob
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )

    # Construct the SAS URL
    sas_url = f"{blob_client.url}?{sas_token}"   
    return sas_url