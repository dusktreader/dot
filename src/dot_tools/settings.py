from pydantic import BaseModel, AnyHttpUrl


class JiraInfo(BaseModel):
    base_url: AnyHttpUrl
    api_key: str

class Settings(BaseModel):
    jira_info: JiraInfo
