# parsers/base.py

from abc import ABC, abstractmethod


PARSER_REGISTRY = {}


class Parser(ABC):
    """
    Base class for all JANR blocklist parsers.
    """

    format_name = None  # must be overridden
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # ignore base class itself
        if cls.format_name is None:
            return

        name = cls.format_name.lower()
        if name in PARSER_REGISTRY:
            raise ValueError(f"Duplicate parser registered: {name}")

        PARSER_REGISTRY[name] = cls

    @abstractmethod
    def parse(self, lines) -> set[str]:
        pass