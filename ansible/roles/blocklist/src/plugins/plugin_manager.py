#!/usr/bin/env python3

import importlib
import inspect
import pkgutil
from pathlib import Path

from core.janr_logger import logger

ALLOWED_CATEGORIES = {"feed", "dataset", "parser"}


class PluginManager:
    _plugins = {}

    # -----------------------------
    # registration
    # -----------------------------

    @classmethod
    def register(cls, plugin_cls):

        category = getattr(plugin_cls, "plugin_category", None)
        name = getattr(plugin_cls, "plugin_name", None)

        logger.log(
            f"Registering plugin: category={category} name={name} class={plugin_cls}"
        )

        if not category or not name:
            raise ValueError(f"Plugin missing metadata: {plugin_cls}")

        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Disallowed plugin category: {category} ({plugin_cls})")

        cls._plugins.setdefault(category, {})
        cls._plugins[category][name] = plugin_cls

    # -----------------------------
    # discovery
    # -----------------------------

    @classmethod
    def discover(cls, package_name: str):
        """
        Auto-discover plugins in a package
        and register them.
        """
        logger.log(f"pluginmanager discover: {package_name}")

        package = importlib.import_module(package_name)
        logger.log(f"discover package: {package}")
        try:
            package_path = Path(package.__file__).parent
        except Exception as e:
            logger.log(f"Unable to create package_path: {e}")

        for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
            logger.log(f"Found module: {module_name}")
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)
            logger.log(f"Imported module: {full_module_name}")

            for _, obj in inspect.getmembers(
                module,
                inspect.isclass,
            ):
                # ensure class belongs to
                # this module only
                if obj.__module__ != full_module_name:
                    continue

                logger.log(
                    f"Found class "
                    f"{obj.__name__} "
                    f"abstract={inspect.isabstract(obj)} "
                    f"module={obj.__module__}"
                )
                # skip abstract classes
                if inspect.isabstract(obj):
                    continue

                # must expose metadata
                if not getattr(obj, "plugin_name", None):
                    continue

                if not getattr(obj, "plugin_category", None):
                    continue

                cls.register(obj)

    # -----------------------------
    # resolution
    # -----------------------------

    @classmethod
    def get(cls, category: str, name: str):

        try:
            return cls._plugins[category][name]

        except KeyError:
            raise ValueError(f"Unknown plugin: category={category}, name={name}")

    # -----------------------------
    # convenience helpers
    # -----------------------------

    @classmethod
    def feed(cls, name: str):
        return cls.get("feed", name)

    @classmethod
    def dataset(cls, name: str):
        return cls.get("dataset", name)

    @classmethod
    def parser(cls, name: str):
        return cls.get("parser", name)

    # -----------------------------
    # debug
    # -----------------------------

    @classmethod
    def list_plugins(cls):
        return cls._plugins
