from azure.functions import HttpRequest, HttpResponse
import os
import json

def authorize(func):
    def wrapper(req: HttpRequest):  # Fixed type hint to directly use HttpRequest
        token = req.headers.get("X-Gitlab-Token")
        expected_token = os.getenv("GITLAB_WEBHOOK_SECRET_TOKEN")
        
        if token != expected_token or req.method != "POST":
            return HttpResponse(
                json.dumps({"error": "Forbidden"}),
                status_code=403,
                mimetype="application/json"
            )

        return func(req)

    return wrapper