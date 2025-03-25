from pydantic import BaseModel
import json

class WebhookModel(BaseModel):
    object_kind: str
    projectname: str
    wikiTitle: str
    wikiContent: str
    wikiAction: str

    def to_json(self):
        return json.dumps(self.model_dump())
