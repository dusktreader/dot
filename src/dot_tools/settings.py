from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, Field
from typerdrive import PlaintextSecretStr


class CredentialsModel(BaseModel):
    """Store credentials for personal services."""
    gmail_client_id: PlaintextSecretStr = Field(default=PlaintextSecretStr(""), description="Gmail OAuth client ID")
    gmail_client_secret: PlaintextSecretStr = Field(default=PlaintextSecretStr(""), description="Gmail OAuth client secret")
    jira_api_key: PlaintextSecretStr = Field(default=PlaintextSecretStr(""), description="Jira API key")


class JiraInfo(BaseModel):
    """Jira connection info - used for jira_tools commands"""
    base_url: AnyHttpUrl = Field(default=AnyHttpUrl("https://fusion.jira.com"), description="Jira base URL")
    api_key: str = Field(default="", description="Jira API key")
    cloud_id: str = Field(default="", description="Jira cloud ID")


class SrcMode(str, Enum):
    mine = "mine"
    work = "work"
    others = "others"


class SrcSettings(BaseModel):
    """Source code folder roots used by `dt src`"""
    default_mode: SrcMode = Field(default=SrcMode.mine, description="Mode used when none is given")
    mine_root: str = Field(default="~/src/dusktreader", description="Root for personal source code")
    work_root: str = Field(default="~/src/mhe", description="Root for work source code")
    others_root: str = Field(default="~/src/others", description="Root for other people's source code")


class Settings(BaseModel):
    """Personal application settings"""
    credentials: CredentialsModel = Field(default_factory=CredentialsModel)
    jira_info: JiraInfo = Field(default_factory=JiraInfo, description="Jira connection configuration")
    src: SrcSettings = Field(default_factory=SrcSettings, description="Source folder navigation")
