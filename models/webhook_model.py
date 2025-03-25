from pydantic import BaseModel
import json

class WebhookModel(BaseModel):
    object_kind: str
    projectname: str
    wikiTitle: str
    wikiMarkdownContent: str
    wikiAction: str

    def to_json(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
