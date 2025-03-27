from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import AuthoringClient
import os
import logging
from models.webhook_model import WebhookModel


async def Delete_Knowledge_base(data: WebhookModel):
    
    """
    Deletes a source from the knowledge base.
    This function checks if a source with a specific display name exists in the knowledge base.

    :param data: The WebhookModel containing project and wiki information.
    """

    endpoint = os.environ["LANGUAGE_SERVICE_ENDPOINT"]
    key = os.environ["LANGUAGE_SERVICE_API_KEY"]
    project_name = os.environ["QNA_PROJECT_NAME"]

    client = AuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:

        sources = client.list_sources(
            project_name=project_name
        )

        # check if source display name contains the project name
        source_found = False
        sourceName=""
        display_name = f"{data.projectName} - {data.wikiSlug}"
        try:
            async for source in sources:
                if display_name in source['displayName']:
                    sourceName = source['source']
                    source_found = True
                    break
        except Exception as e:            
            source_found = False
    
        
        if source_found:
            logging.info(f'******* Deleting knowledge base source: {sourceName} .....')
            # Delete the source if found using begin_update_sources with 'delete' operation
            sources_poller = await client.begin_update_sources(
                project_name=project_name,
                sources=[
                    {
                        "op": "delete",
                        "value": {
                            "source": sourceName,
                            "displayName": display_name
                        }
                    }
                ]
            )
            await sources_poller.result()
            logging.info(f'******* Knowledge base source deleted: {sourceName}')

            logging.info(f'******* Deploying project: {project_name} .....')
            poller = await client.begin_deploy_project(
                project_name=project_name,
                deployment_name=os.environ["QNA_DEPLOYMENT_NAME"]
            )
            await poller.result()
            logging.info(f'******* Project deployed: {project_name}')

            return


async def Upsert_Knowledge_base(source_url:str,data: WebhookModel) :
    """    
    Upserts a source into the knowledge base.
    This function adds or updates a source in the knowledge base.    
    It uses the Azure Language Service AuthoringClient to perform the operation.    
    The source URL is expected to be a SAS URL pointing to the blob storage location of the HTML file.
    The function also handles the decoding of the SAS URL to ensure it is in the correct format for the API call.

    :param source_url: The SAS URL of the blob storage location of the HTML file.
    :param data: The WebhookModel containing project and wiki information.

    """
    endpoint = os.environ["LANGUAGE_SERVICE_ENDPOINT"]
    key = os.environ["LANGUAGE_SERVICE_API_KEY"]
    project_name = os.environ["QNA_PROJECT_NAME"]
    display_name = f"{data.projectName} - {data.wikiSlug}"

    # Decode the SAS URL
    decoded_sas_url = source_url.replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('%26', '&')
     
    logging.info(f'******* Upserting knowledge base source : {display_name}')


    client = AuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:

        operation =""       
        if data.wikiAction == "create":
            operation = "add"
        elif data.wikiAction == "update":
            operation = "replace"
            
        else:
            raise ValueError("Invalid wikiAction value. Expected 'add', 'update', or 'delete'.")
        
        sources_poller = await client.begin_update_sources(
        project_name=project_name,
        sources=[
            {
                "op": operation,
                "value": {
                    "displayName": display_name,
                    "source": decoded_sas_url,
                    "sourceUri": decoded_sas_url,
                    "sourceKind": "url"
                }
            }
        ]
        )
        await sources_poller.result()   
        logging.info(f'******* Upserted knowledge base source : {display_name}')

        logging.info(f'******* Deploying project: {project_name} .....')
        poller = await client.begin_deploy_project(
                project_name=project_name,
                deployment_name=os.environ["QNA_DEPLOYMENT_NAME"]
            )
        await poller.result()
        logging.info(f'******* Project deployed: {project_name}')
        
        return


         

