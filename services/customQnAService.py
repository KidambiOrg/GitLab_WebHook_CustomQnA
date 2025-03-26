from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import AuthoringClient
import os

from models.webhook_model import WebhookModel

async def Upsert_Knowledge_base(source_url:str,data: WebhookModel) :
    endpoint = os.environ["LANGUAGE_SERVICE_ENDPOINT"]
    key = os.environ["LANGUAGE_SERVICE_API_KEY"]
    project_name = os.environ["QNA_PROJECT_NAME"]

    # Decode the SAS URL
    decoded_sas_url = source_url.replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('%26', '&')

     

    client = AuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:

        sources = client.list_sources(
            project_name=project_name
        )
        # check if source display name contains the project name
        source_found = False
        display_name = f"{data.projectName} - {data.wikiSlug}"
        try:
            async for source in sources:
                if display_name in source['displayName']:
                    source_found = True
                    break
        except Exception as e:            
            source_found = False

        if not source_found:
            # Add a new source if not found
            add_sources_poller = await client.begin_update_sources(
                project_name=project_name,
                sources=[
                    {
                       "op": "add",
                        "value": {
                            "displayName": display_name,
                            "source": decoded_sas_url,
                            "sourceUri": decoded_sas_url,
                            "sourceKind": "url"
                        }
                    }
                ]
            )
            await add_sources_poller.result()
        else:    
            update_sources_poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "replace",
                    "value": {
                        "displayName": display_name,
                        "source": decoded_sas_url,
                        "sourceUri": decoded_sas_url,
                        "sourceKind": "url"
                    }
                }
            ]
            )
            await update_sources_poller.result()

