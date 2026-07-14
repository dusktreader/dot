from pydantic import AnyHttpUrl, BaseModel, Field, SecretStr, field_serializer


class CredentialsModel(BaseModel):
    """Store credentials for personal services."""
    gmail_client_id: SecretStr = Field(default=SecretStr(""), description="Gmail OAuth client ID")
    gmail_client_secret: SecretStr = Field(default=SecretStr(""), description="Gmail OAuth client secret")
    jira_api_key: SecretStr = Field(default=SecretStr(""), description="Jira API key")

    @field_serializer("gmail_client_id", "gmail_client_secret", "jira_api_key", when_used="json")
    def serialize_credential(self, value: SecretStr) -> str:
        """Preserve credential values when Typerdrive serializes nested settings."""
        return value.get_secret_value()


class JiraInfo(BaseModel):
    """Jira connection info - used for jira_tools commands"""
    base_url: AnyHttpUrl = Field(default=AnyHttpUrl("https://fusion.jira.com"), description="Jira base URL")
    api_key: str = Field(default="", description="Jira API key")
    cloud_id: str = Field(default="", description="Jira cloud ID")


class Settings(BaseModel):
    """Personal application settings"""
    credentials: CredentialsModel = Field(default_factory=CredentialsModel)
    jira_info: JiraInfo = Field(default_factory=JiraInfo, description="Jira connection configuration")
