"""Application settings and environment management via Pydantic Settings."""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # App Information
    app_name: str = "NEXUS Flow AI"
    app_version: str = "2.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    secret_key: str = Field(
        default="nexus_flow_super_secure_secret_key_change_in_production_32chars",
        env="SECRET_KEY",
    )

    # Operational Mode (Mock vs Live)
    live_mode: bool = Field(default=False, env="LIVE_MODE")

    # Persistence
    database_url: str = Field(default="sqlite:///./nexus_flow.db", env="DATABASE_URL")

    # OpenAI API
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_vision_model: str = Field(default="gpt-4o", env="OPENAI_VISION_MODEL")
    openai_timeout_seconds: float = Field(default=8.0, env="OPENAI_TIMEOUT_SECONDS")

    # Airtable
    airtable_api_key: Optional[str] = Field(default=None, env="AIRTABLE_API_KEY")
    airtable_base_id: Optional[str] = Field(default=None, env="AIRTABLE_BASE_ID")
    airtable_leads_table: str = Field(default="Leads", env="AIRTABLE_LEADS_TABLE")
    airtable_projects_table: str = Field(default="Projects", env="AIRTABLE_PROJECTS_TABLE")

    # Slack
    slack_bot_token: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    slack_default_channel: str = Field(default="#ops-alerts", env="SLACK_DEFAULT_CHANNEL")
    slack_sales_channel: str = Field(default="#sales-leads", env="SLACK_SALES_CHANNEL")
    slack_support_channel: str = Field(default="#support-triage", env="SLACK_SUPPORT_CHANNEL")

    # Stripe
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(
        default="whsec_mock_signing_secret_for_local_testing",
        env="STRIPE_WEBHOOK_SECRET",
    )

    # Google Sheets
    google_sheets_credentials_json: Optional[str] = Field(
        default=None, env="GOOGLE_SHEETS_CREDENTIALS_JSON"
    )
    google_sheets_spreadsheet_id: Optional[str] = Field(
        default=None, env="GOOGLE_SHEETS_SPREADSHEET_ID"
    )

    # Email
    email_provider: str = Field(default="mock", env="EMAIL_PROVIDER")
    email_draft_only: bool = Field(default=True, env="EMAIL_DRAFT_ONLY")

    # Performance & Tolerance SLAs
    lead_sla_max_seconds: float = Field(default=10.0, env="LEAD_SLA_MAX_SECONDS")
    invoice_tolerance_cents: int = Field(default=1, env="INVOICE_TOLERANCE_CENTS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
