#!/usr/bin/env python3

from abc import ABC, abstractmethod
from pathlib import Path

from core.janr_logger import logger


class Feed(ABC):
    plugin_category = "feed"
    plugin_name = None

    DOWNLOAD_DIR = Path("/run/janr/blocklist/artifacts/downloads")

    def __init__(self):
        self.logger = logger

        # ensure base download directory exists
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # required interface
    # -----------------------------

    @abstractmethod
    def fetch(self, asset):
        """
        Fetch raw data for an asset.

        Must return:
            Path to downloaded dataset file
        """
        pass

    # -----------------------------
    # shared helper utilities
    # -----------------------------

    def dataset_path(self, asset, suffix="raw") -> Path:
        """
        Standardized download location for feeds.
        """

        filename = f"{asset.id}.{suffix}"
        return self.DOWNLOAD_DIR / filename

    # -----------------------------
    # logging helpers (optional convenience)
    # -----------------------------

    def log(self, msg, lvl=logger.INFO):
        self.logger.log(f"[feed:{self.plugin_name}] {msg}", lvl)
