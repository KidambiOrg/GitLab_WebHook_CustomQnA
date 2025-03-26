import os
from azure.storage.queue import BinaryBase64EncodePolicy,QueueServiceClient 
from models.webhook_model import WebhookModel


def add_to_queue(webhook_model: WebhookModel):

    """
    Add a webhook model to the Azure Queue.
    This function serializes the webhook model to JSON and sends it to the Azure Queue.
    
    :param webhook_model: The WebhookModel instance to be added to the queue.

    """


    # Get the connection string and queue name from environment variables
    connection_string = os.getenv('WEBHOOK_STORAGE')
    queue_name = os.getenv('QUEUE_NAME')
    queue_client = QueueServiceClient.from_connection_string(conn_str=connection_string).get_queue_client(queue=queue_name)
    queue_client.message_encode_policy = BinaryBase64EncodePolicy()
    queue_client.send_message( queue_client.message_encode_policy.encode(content=webhook_model.model_dump_json().encode('ascii'))   )
    