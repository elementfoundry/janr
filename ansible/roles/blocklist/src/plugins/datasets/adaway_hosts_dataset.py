#!/usr/bin/env python3

from .base_dataset import Dataset


class AdAwayHostsDataset(Dataset):
    plugin_name = "adaway_hosts_dataset"

    def records(self):
        """
        Parse AdAway hosts file format:

            0.0.0.0 example.com
            127.0.0.1 example.org
            # comments

        Output:
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

                # strip comments
                if line.startswith("#"):
                    continue

                # hosts format: IP DOMAIN
                parts = line.split()

                if len(parts) < 2:
                    continue

                domain = parts[1].strip().lower()

                if not domain:
                    continue

                # safety cleanup
                if domain in ("localhost", "localhost.localdomain"):
                    continue

                yield {
                    "ioc": domain,
                    "ioc_type": "domain",
                }
