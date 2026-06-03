#!/usr/bin/env python3

import requests

from .base_feed import Feed


class URLHausFeed(Feed):
    plugin_name = "urlhaus_feed"

    URL = "https://urlhaus.abuse.ch/downloads/rpz/"

    def fetch(self, asset):
        """
        Fetch raw RPZ feed from URLHaus.

        URLHaus already returns RPZ-formatted data,
        so we just persist it as-is.
        """

        output_path = self.dataset_path(asset, "rpz")

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
