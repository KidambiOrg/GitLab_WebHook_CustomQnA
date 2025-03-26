import requests
from models.webhook_model import WebhookModel
import os
 
def fetch_gitlab_wiki_content(webhook_model: WebhookModel):
    """
    Fetches the content of a GitLab wiki page using the GitLab API.

    Args:
        webhook_model (WebhookModel): The webhook model containing projectId and wikislug.

    Returns:
        str: The content of the wiki page.
    """
    # Get the base URL and private token from app settings
    gitlab_api_url = os.getenv('GITLAB_API_URL')
    private_token = os.getenv('GITLAB_API_TOKEN')

    # Replace placeholders in the URL with actual values from the webhook model
    url = gitlab_api_url.replace('{projectId}', webhook_model.projectId).replace('{wikislug}', webhook_model.wikiSlug)

    # Set up headers for the request
    headers = {
        'Authorization': f"Bearer {private_token}"
    }

    # Make the GET request to the GitLab API
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Extract and return the "content" from the response
    return response.json().get('content')


