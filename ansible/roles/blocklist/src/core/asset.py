#!/usr/bin/env python3

from pathlib import Path

from plugins.plugin_manager import PluginManager

from core.artifact_registry import artifact_registry
from core.logger import logger


class Asset:
    def __init__(self, config, blocklist_id: str):
        logger.log(f"Creating Asset: {config}")
        self.config = config
        self.blocklist_id = blocklist_id
        self._init_plugins()

    def __getattr__(self, name):
        try:
            return getattr(self.config, name)
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__!s} has no attribute '{name}'"
            ) from None

    def _init_plugins(self):
        logger.log(f"Initializing plugins for asset {self.id}")
        feed_cls = PluginManager.feed(self.feed_name)
        dataset_cls = PluginManager.dataset(self.dataset_name)
        parser_cls = PluginManager.parser(self.parser_name)

        self.feed_instance = feed_cls()
        self.dataset_cls = dataset_cls
        self.parser_instance = parser_cls(asset=self)

        artifact_registry.register(
            self.blocklist_id,
            self.preserve_artifacts,
        )

    def run(self):
        dataset_path = self.feed_instance.fetch(self)
        try:
            self.dataset = self.dataset_cls(dataset_path)
            return self.finalize()
        finally:
            self._cleanup_artifact(dataset_path)

    def _cleanup_artifact(self, dataset_path):
        if artifact_registry.should_preserve(self.blocklist_id):
            logger.log(
                f"Preserving artifact for blocklist {self.blocklist_id}: {dataset_path}"
            )
            return
        try:
            Path(dataset_path).unlink(missing_ok=True)
            logger.log(f"Removed artifact: {dataset_path}")
        except Exception as e:
            logger.log(
                f"Failed to remove artifact {dataset_path}: {e}",
                logger.ERROR,
            )

    def finalize(self):
        domains = set()
        if self.dataset is None:
            raise RuntimeError(f"Dataset not initialized for asset {self.id}")
        if self.parser_instance is None:
            raise RuntimeError(f"Parser not initialized for asset {self.id}")
        for record in self.dataset.records():
            try:
                value = self.parser_instance.process(record)
            except Exception as e:
                logger.log(f"Parser error: {e}", logger.ERROR)
                continue
            if value:
                domains.add(value)
        return domains
