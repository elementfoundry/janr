#!/usr/bin/env python3

from .base_dataset import Dataset


class URLHausRPZDataset(Dataset):
    plugin_name = "urlhaus_rpz_dataset"

    def records(self):
        """
        Parse URLHaus RPZ file into structured IOC records.

        Input format contains:
            - RPZ metadata ($TTL, SOA, NS)
            - comments (; ...)
            - domain CNAME rules

        Output format:
            {
                "ioc": "<domain>",
                "ioc_type": "domain"
            }
        """

        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                # strip inline comments early for efficiency
                if ";" in line:
                    line = line.split(";", 1)[0].strip()

                if not line:
                    continue

                # ignore RPZ metadata lines
                if line.startswith("$"):
                    continue

                # ignore SOA / NS / zone boilerplate
                upper = line.upper()
                if "SOA" in upper or "NS" in upper:
                    continue

                parts = line.split()

                # expected: domain CNAME .
                if len(parts) < 3:
                    continue

                domain = parts[0].strip().lower()

                # safety filters for malformed or junk entries
                if not domain:
                    continue

                if domain == ".":
                    continue

                if "rpz.urlhaus.abuse.ch" in domain:
                    continue

                if domain == "localhost":
                    continue

                yield {
                    "ioc": domain,
                    "ioc_type": "domain",
                }
