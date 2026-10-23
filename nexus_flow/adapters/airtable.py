"""Airtable integration adapter with mock simulation and live REST capabilities."""

import time
import uuid
from typing import Any, Dict, List, Optional
import httpx
from nexus_flow.adapters.base import BaseAdapter
from nexus_flow.core.logging import logger

class AirtableAdapter(BaseAdapter):
    """Handles synchronization of leads and projects with Airtable bases."""

    def __init__(self):
        super().__init__(service_name="Airtable")
        self.mock_store: Dict[str, Dict[str, Any]] = {}

    def health_check(self) -> Dict[str, Any]:
        if not self.is_live_mode:
            return {
                "status": "ready (mock)",
                "live": False,
                "configured": bool(self.settings.airtable_api_key and self.settings.airtable_base_id),
            }
        if not self.settings.airtable_api_key or not self.settings.airtable_base_id:
            return {"status": "unconfigured", "live": True, "error": "Missing API Key or Base ID"}
        try:
            url = f"https://api.airtable.com/v0/{self.settings.airtable_base_id}/{self.settings.airtable_leads_table}?maxRecords=1"
            headers = {"Authorization": f"Bearer {self.settings.airtable_api_key}"}
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url, headers=headers)
                return {
                    "status": "connected" if res.status_code == 200 else f"error ({res.status_code})",
                    "live": True,
                }
        except Exception as e:
            return {"status": "unreachable", "live": True, "error": str(e)}

    def create_or_update_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates or updates a lead record in Airtable."""
        return self.execute_with_telemetry(
            "create_or_update_lead", self._create_or_update_lead_impl, lead_data
        )

    def _create_or_update_lead_impl(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_live_mode or not self.settings.airtable_api_key:
            record_id = f"rec_mock_{uuid.uuid4().hex[:10]}"
            self.mock_store[record_id] = lead_data
            time.sleep(0.04)  # realistic API latency
            logger.info(f"[MOCK] Airtable lead record created: {record_id}")
            return {
                "success": True,
                "record_id": record_id,
                "mode": "mock",
                "fields": lead_data,
            }

        url = f"https://api.airtable.com/v0/{self.settings.airtable_base_id}/{self.settings.airtable_leads_table}"
        headers = {
            "Authorization": f"Bearer {self.settings.airtable_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"fields": lead_data}
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "record_id": data.get("id"),
                "mode": "live",
                "fields": data.get("fields", {}),
            }

    def create_or_update_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates or updates a project record in Airtable."""
        if not self.is_live_mode or not self.settings.airtable_api_key:
            record_id = f"rec_proj_{uuid.uuid4().hex[:10]}"
            self.mock_store[record_id] = project_data
            return {
                "success": True,
                "record_id": record_id,
                "mode": "mock",
                "fields": project_data,
            }

        url = f"https://api.airtable.com/v0/{self.settings.airtable_base_id}/{self.settings.airtable_projects_table}"
        headers = {
            "Authorization": f"Bearer {self.settings.airtable_api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, headers=headers, json={"fields": project_data})
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "record_id": data.get("id"),
                "mode": "live",
                "fields": data.get("fields", {}),
            }
