# parsers/__init__.py

import importlib
import pkgutil
import pathlib

from .base import PARSER_REGISTRY


def discover_parsers():

    package_dir = pathlib.Path(__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):

        # skip base module
        if module_name == "base":
            continue

        importlib.import_module(f"parsers.{module_name}")


# auto-run on import
discover_parsers()