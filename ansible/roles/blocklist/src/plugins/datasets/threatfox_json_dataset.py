#!/usr/bin/env python3

import json

from .base_dataset import Dataset


class ThreatFoxJSONDataset(Dataset):
    plugin_name = "threatfox_json_dataset"

    def records(self):
        """
        ThreatFox JSON structure:

        {
            "query_status": "ok",
            "data": [
                {...},
                {...}
            ]
        }
        """

        with open(
            self.path,
            "r",
            encoding="utf-8",
        ) as f:
            document = json.load(f)

        if not isinstance(document, dict):
            return

        records = document.get("data", [])

        if not isinstance(records, list):
            return

        for record in records:
            if not isinstance(record, dict):
                continue

            yield record
