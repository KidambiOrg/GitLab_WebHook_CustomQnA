import azure.functions as func
import logging
from models.webhook_model import WebhookModel
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="ParseFile", methods=["POST"])
def ParseFile(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        webhook_data = WebhookModel(**req_body)
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON"}), status_code=400, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

    return func.HttpResponse(webhook_data.to_json(), status_code=200, mimetype="application/json")