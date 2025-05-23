from pydantic import BaseModel, AnyHttpUrl


class JiraInfo(BaseModel):
    base_url: AnyHttpUrl
    api_key: str
    cloud_id: str

class Settings(BaseModel):
    jira_info: JiraInfo
