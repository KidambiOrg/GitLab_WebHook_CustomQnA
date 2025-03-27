import azure.functions as func
import logging
from handlers.authheaderhandler import authorize
from models.webhook_model import WebhookModel
import json
import os
from services.AzureBlobStorage import delete_blob, upload_string_and_generate_sas
from services.AzureQueueService import add_to_queue
from services.CustomQnAService import Delete_Knowledge_base, Upsert_Knowledge_base
from services.GitlabServices import  fetch_gitlab_wiki_content

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="ParseFile", methods=["POST"])
@authorize
def ParseFile(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')
 
    try:
        req_body = req.get_json()
        webhook_data =  WebhookModel.model_validate_json(json.dumps(req_body))
        add_to_queue(webhook_data)
    except ValueError as e:
        logging.error(f"ValueError: {e}")       
        return func.HttpResponse(json.dumps({"error": "Invalid JSON"}), status_code=400, mimetype="application/json")
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

    return func.HttpResponse("OK", status_code=200, mimetype="application/json")


@app.queue_trigger(arg_name="azqueue", queue_name=os.getenv("QUEUE_NAME"),
                               connection="WEBHOOK_STORAGE") 
async def WikiEventQueueParser(azqueue: func.QueueMessage):
    logging.info('Python Queue trigger processed a message: %s',
                azqueue.get_body().decode('utf-8'))
    
    # Parse the message and add to queue
    message_body = azqueue.get_body().decode('utf-8')
    webhook_data = WebhookModel.model_validate_json(message_body)

    if webhook_data.wikiAction == "delete":
        # Delete the source from the knowledge base        
        await Delete_Knowledge_base( webhook_data)

        # delete the blob from the blob storage
        await delete_blob(webhook_data)
      

    else:
        html  = await fetch_gitlab_wiki_content(webhook_data)

        # now we can upload the html to blob storage and get the blob sas url
        blob_url = await upload_string_and_generate_sas(html,webhook_data)

        # now call the Upsert_Knowledge_base function to add the blob url to the knowledge base
        await Upsert_Knowledge_base(blob_url, webhook_data)

    logging.info('------------------ !!! DONE !!! ------------------')

 