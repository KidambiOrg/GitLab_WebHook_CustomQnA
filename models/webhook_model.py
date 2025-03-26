from pydantic import BaseModel
import json

class WebhookModel(BaseModel):
    objectKind: str
    projectName: str
    projectId: str
    wikiSlug: str
    wikiAction:str

    def to_json(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
