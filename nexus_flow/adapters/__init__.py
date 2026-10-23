"""Integration adapters package."""

from nexus_flow.adapters.base import BaseAdapter
from nexus_flow.adapters.airtable import AirtableAdapter
from nexus_flow.adapters.slack import SlackAdapter
from nexus_flow.adapters.stripe import StripeAdapter
from nexus_flow.adapters.sheets import GoogleSheetsAdapter
from nexus_flow.adapters.email import EmailAdapter

__all__ = [
    "BaseAdapter",
    "AirtableAdapter",
    "SlackAdapter",
    "StripeAdapter",
    "GoogleSheetsAdapter",
    "EmailAdapter",
]
