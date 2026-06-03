#!/usr/bin/env python3

from .base_parser import Parser


class ThreatFoxParser(Parser):
    plugin_name = "threatfox_parser"

    def valid(self, record):
        """
        Only accept high-confidence domain IOCs.
        """

        if record.get("ioc_type") != "domain":
            return False

        confidence = record.get("confidence_level")

        try:
            return int(confidence) >= 75
        except (TypeError, ValueError):
            return False

    def parse(self, record):
        """
        Extract and normalize domain IOC.
        """

        domain = record.get("ioc")

        if not domain:
            return None

        domain = domain.strip().lower()

        if not domain:
            return None

        return domain
