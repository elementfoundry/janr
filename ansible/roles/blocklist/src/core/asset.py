#!/usr/bin/env python3

from pathlib import Path

from plugins.plugin_manager import PluginManager

from core.janr_logger import logger


class Asset:
    def __init__(self, config):

        logger.log(f"Creating Asset: {config}")

        self.config = config

        self.id = config.id
        self.feed_name = config.feed
        self.dataset_name = config.dataset
        self.parser_name = config.parser

        self.preserve_artifacts = config.preserve_artifacts

        if not isinstance(self.preserve_artifacts, bool):
            raise TypeError(f"Asset {self.id}: preserve_artifacts must be a boolean")

        self.feed = None
        self.dataset = None
        self.parser = None
        self.dataset_cls = None

        self._init_plugins()

    # -----------------------------
    # plugin wiring
    # -----------------------------

    def _init_plugins(self):

        logger.log(f"Initializing plugins for asset {self.id}")

        feed_cls = PluginManager.feed(self.feed_name)

        dataset_cls = PluginManager.dataset(self.dataset_name)

        parser_cls = PluginManager.parser(self.parser_name)

        self.feed = feed_cls()
        self.dataset_cls = dataset_cls
        self.parser = parser_cls(asset=self)

    # -----------------------------
    # execution lifecycle
    # -----------------------------

    def run(self):

        dataset_path = self.feed.fetch(self)

        try:
            self.dataset = self.dataset_cls(dataset_path)

            return self.finalize()

        finally:
            self._cleanup_artifact(dataset_path)

    # -----------------------------
    # artifact cleanup
    # -----------------------------

    def _cleanup_artifact(self, dataset_path):

        if self.preserve_artifacts:
            logger.log(f"Preserving artifact for asset {self.id}: {dataset_path}")

            return

        try:
            Path(dataset_path).unlink(missing_ok=True)

            logger.log(f"Removed artifact for asset {self.id}: {dataset_path}")

        except Exception as e:
            logger.log(
                f"Failed to remove artifact {dataset_path}: {e}",
                logger.ERROR,
            )

    # -----------------------------
    # finalization step
    # -----------------------------

    def finalize(self):

        domains = set()

        if not self.dataset:
            raise RuntimeError(f"Dataset not initialized for asset {self.id}")

        if not self.parser:
            raise RuntimeError(f"Parser not initialized for asset {self.id}")

        for record in self.dataset.records():
            try:
                value = self.parser.process(record)

            except Exception as e:
                logger.log(
                    f"Parser error: {e}",
                    logger.ERROR,
                )

                continue

            if value:
                domains.add(value)

        return domains
