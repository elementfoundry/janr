#!/usr/bin/env python3

from pathlib import Path

import requests

from .base_feed import Feed


class ThreatFoxFeed(Feed):
    plugin_name = "threatfox_feed"

    URL = "https://threatfox-api.abuse.ch/api/v1/"

    CRED_NAME = "janr_threatfox"
    SYSTEMD_UNIT = "janr-blocklists.service"

    def _get_api_key(self):
        """
        ThreatFox is a credentialed feed using systemd credentials.
        """

        cred_path = Path("/run/credentials") / self.SYSTEMD_UNIT / self.CRED_NAME

        if not cred_path.exists():
            raise RuntimeError(f"Missing systemd credential for ThreatFox: {cred_path}")

        return cred_path.read_text(encoding="utf-8").strip()

    def fetch(self, asset):

        output_path = self.dataset_path(asset, "json")

        api_key = self._get_api_key()

        headers = {
            "Auth-Key": api_key,
        }

        payload = {
            "query": "get_iocs",
            "days": 7,
        }

        response = requests.post(
            self.URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        output_path.write_text(response.text, encoding="utf-8")

        return output_path
