from abc import ABC, abstractmethod

class Format(ABC):

    plugin_name = None
    plugin_category = "format"

    @abstractmethod
    def mutate(self, raw_data):
        """
        Convert raw input into iterable records.
        """
        pass