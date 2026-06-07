#!/usr/bin/env python3

from abc import ABC, abstractmethod

from core.logger import logger


class Dataset(ABC):
    plugin_category = "dataset"
    plugin_name = None

    def __init__(self, path):

        self.path = path
        self.logger = logger

        self.logger.log(
            f"[dataset:{self.plugin_name}] initialized: {self.path}", logger.DEBUG
        )

    # -----------------------------
    # required interface
    # -----------------------------

    @abstractmethod
    def records(self):
        """
        Yield parsed records from dataset file.
        """
        pass

    # -----------------------------
    # shared helpers
    # -----------------------------

    def exists(self):
        return self.path.exists()

    def log(self, msg, lvl=logger.INFO):
        self.logger.log(f"[dataset:{self.plugin_name}] {msg}", lvl)
