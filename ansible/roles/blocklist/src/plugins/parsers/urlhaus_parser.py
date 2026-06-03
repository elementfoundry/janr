#!/usr/bin/env python3

from .base_parser import Parser


class URLHausParser(Parser):
    plugin_name = "urlhaus_parser"

    def valid(self, record):
        """
        Final validation layer for URLHaus domains.

        Dataset already:
        - strips comments
        - removes RPZ metadata
        - filters obvious noise

        Here we only enforce domain sanity.
        """

        domain = record.get("ioc")

        if not domain:
            return False

        domain = domain.strip().lower()

        if not domain:
            return False

        # safety / noise guards
        if domain.startswith("$"):
            return False

        if domain == ".":
            return False

        if "rpz.urlhaus.abuse.ch" in domain:
            return False

        if domain == "localhost":
            return False

        return True

    def parse(self, record):
        """
        Normalize IOC into final domain string.
        """

        domain = record.get("ioc")

        if not domain:
            return None

        domain = domain.strip().lower()

        if not domain:
            return None

        # final defensive cleanup (dataset should already handle most of this)
        if domain.startswith("$"):
            return None

        if domain == ".":
            return None

        if "rpz.urlhaus.abuse.ch" in domain:
            return None

        if domain == "localhost":
            return None

        return domain
