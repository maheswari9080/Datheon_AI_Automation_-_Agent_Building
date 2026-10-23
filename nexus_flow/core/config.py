"""Application settings and environment management via Pydantic Settings."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App Information
    app_name: str = "NEXUS Flow AI"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"
    secret_key: str = "nexus_flow_super_secure_secret_key_change_in_production_32chars"

    # Operational Mode (Mock vs Live)
    live_mode: bool = False

    # Persistence
    database_url: str = "sqlite:///./nexus_flow.db"

    # OpenAI API
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_vision_model: str = "gpt-4o"
    openai_timeout_seconds: float = 8.0

    # Airtable
    airtable_api_key: Optional[str] = None
    airtable_base_id: Optional[str] = None
    airtable_leads_table: str = "Leads"
    airtable_projects_table: str = "Projects"

    # Slack
    slack_bot_token: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    slack_default_channel: str = "#ops-alerts"
    slack_sales_channel: str = "#sales-leads"
    slack_support_channel: str = "#support-triage"

    # Stripe
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: str = "whsec_mock_signing_secret_for_local_testing"

    # Google Sheets
    google_sheets_credentials_json: Optional[str] = None
    google_sheets_spreadsheet_id: Optional[str] = None

    # Email
    email_provider: str = "mock"
    email_draft_only: bool = True

    # Performance & Tolerance SLAs
    lead_sla_max_seconds: float = 10.0
    invoice_tolerance_cents: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
