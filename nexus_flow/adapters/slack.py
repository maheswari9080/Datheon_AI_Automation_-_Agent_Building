"""Slack integration adapter for notifications, channel creation, and team alerts."""

import time
from typing import Any, Dict, List, Optional
import httpx
from nexus_flow.adapters.base import BaseAdapter
from nexus_flow.core.logging import logger

class SlackAdapter(BaseAdapter):
    """Handles posting rich messages and provisioning project collaboration channels."""

    def __init__(self):
        super().__init__(service_name="Slack")
        self.sent_messages: List[Dict[str, Any]] = []
        self.created_channels: List[str] = ["#ops-alerts", "#sales-leads", "#support-triage"]

    def health_check(self) -> Dict[str, Any]:
        if not self.is_live_mode:
            return {
                "status": "ready (mock)",
                "live": False,
                "configured": bool(self.settings.slack_webhook_url or self.settings.slack_bot_token),
            }
        if not self.settings.slack_webhook_url and not self.settings.slack_bot_token:
            return {"status": "unconfigured", "live": True, "error": "Missing webhook URL or bot token"}
        return {"status": "configured", "live": True}

    def send_notification(
        self,
        channel: str,
        title: str,
        message: str,
        priority: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Dispatches an alert to the designated Slack channel."""
        return self.execute_with_telemetry(
            "send_notification",
            self._send_notification_impl,
            channel,
            title,
            message,
            priority,
            metadata,
        )

    def _send_notification_impl(
        self,
        channel: str,
        title: str,
        message: str,
        priority: str,
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        emoji_map = {
            "HOT": ":fire:",
            "CRITICAL": ":rotating_light:",
            "HIGH": ":warning:",
            "INFO": ":information_source:",
            "SUCCESS": ":white_check_mark:",
        }
        emoji = emoji_map.get(priority.upper(), ":bell:")

        payload = {
            "channel": channel,
            "text": f"{emoji} *{title}*\n{message}",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"{title}", "emoji": True},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"{emoji} *Status/Priority:* {priority}\n{message}"},
                },
            ],
        }

        if metadata:
            fields = [
                {"type": "mrkdwn", "text": f"*{k}:*\n{v}"}
                for k, v in list(metadata.items())[:8]
            ]
            payload["blocks"].append({"type": "section", "fields": fields})

        if not self.is_live_mode or not self.settings.slack_webhook_url:
            record = {
                "channel": channel,
                "title": title,
                "priority": priority,
                "payload": payload,
                "timestamp": time.time(),
                "mode": "mock",
            }
            self.sent_messages.append(record)
            time.sleep(0.03)
            logger.info(f"[MOCK] Slack alert dispatched to {channel}: {title}")
            return {"success": True, "channel": channel, "mode": "mock"}

        # Live Webhook Post
        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.post(self.settings.slack_webhook_url, json=payload)
                res.raise_for_status()
                return {"success": True, "channel": channel, "mode": "live"}
        except Exception as e:
            logger.error(f"Failed to post to live Slack webhook: {e}")
            return {"success": False, "channel": channel, "error": str(e), "mode": "live"}

    def provision_project_channel(self, project_code: str) -> Dict[str, Any]:
        """Creates or registers a dedicated Slack channel for a customer project."""
        clean_code = project_code.lower().replace("_", "-")
        channel_name = f"#proj-{clean_code}"
        if channel_name not in self.created_channels:
            self.created_channels.append(channel_name)
        logger.info(f"Slack project collaboration channel mapped: {channel_name}")
        return {"success": True, "channel": channel_name, "mode": "live" if self.is_live_mode else "mock"}
