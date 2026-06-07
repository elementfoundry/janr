#!/usr/bin/env python3

from abc import ABC, abstractmethod

from core.logger import logger


class Parser(ABC):
    plugin_category = "parser"
    plugin_name = None

    def __init__(self, asset=None):

        self.asset = asset
        self.logger = logger

        self.logger.log(f"[parser:{self.plugin_name}] initialized", logger.DEBUG)

    # -----------------------------
    # required interface
    # -----------------------------

    @abstractmethod
    def parse(self, record):
        """
        Convert a dataset record into a normalized value.

        Return:
            - value (e.g. domain, ip, url)
            - or None if record should be ignored
        """
        pass

    # -----------------------------
    # optional lifecycle hooks
    # -----------------------------

    def valid(self, record):
        """
        Pre-filter hook before parsing.

        Default: accept everything.
        """
        return True

    def process(self, record):
        """
        Standard execution entrypoint:

        validate → parse
        """

        if not self.valid(record):
            return None

        try:
            return self.parse(record)

        except Exception as e:
            self.logger.log(
                f"[parser:{self.plugin_name}] error parsing record: {e}", logger.WARNING
            )

            return None

    # -----------------------------
    # logging helper
    # -----------------------------

    def log(self, msg, lvl=logger.INFO):
        self.logger.log(f"[parser:{self.plugin_name}] {msg}", lvl)
