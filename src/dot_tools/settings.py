from pydantic import BaseModel, AnyHttpUrl


class JiraInfo(BaseModel):
    baseurl: AnyHttpUrl
    username: str
    password: str

class Settings(BaseModel):
    jira_info: JiraInfo | None = None
