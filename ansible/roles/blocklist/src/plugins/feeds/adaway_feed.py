#!/usr/bin/env python3

import requests

from .base_feed import Feed


class AdAwayFeed(Feed):
    plugin_name = "adaway_feed"

    URL = "https://adaway.org/hosts.txt"

    def fetch(self, asset):
        """
        Fetch AdAway hosts file (plain text).
        """

        output_path = self.dataset_path(asset, "txt")

        response = requests.get(
            self.URL,
            timeout=30,
        )

        response.raise_for_status()

        output_path.write_text(
            response.text,
            encoding="utf-8",
        )

        return output_path
