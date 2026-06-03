#!/usr/bin/env python3

from .base_parser import Parser


class AdAwayParser(Parser):
    plugin_name = "adaway_parser"

    def valid(self, record):
        """
        Accept only valid domain-shaped IOCs.
        """

        domain = record.get("ioc")

        if not domain:
            return False

        domain = domain.strip().lower()

        if not domain:
            return False

        if domain.startswith("#"):
            return False

        if domain in ("localhost", "localhost.localdomain"):
            return False

        return True

    def parse(self, record):
        """
        Normalize domain IOC.
        """

        domain = record.get("ioc")

        if not domain:
            return None

        domain = domain.strip().lower()

        if not domain:
            return None

        if domain.startswith("#"):
            return None

        if domain in ("localhost", "localhost.localdomain"):
            return None

        return domain
