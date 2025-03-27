import aiohttp
from models.webhook_model import WebhookModel
import os

async def fetch_gitlab_wiki_content(webhook_model: WebhookModel):
    """
    Fetches the content of a GitLab wiki page using the GitLab API asynchronously.

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

    # Make the GET request to the GitLab API asynchronously
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise an exception for HTTP errors
            # Extract and return the "content" from the response
            json_response = await response.json()
            return json_response.get('content')


