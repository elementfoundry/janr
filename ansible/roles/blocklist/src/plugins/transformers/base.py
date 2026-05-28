from abc import ABC, abstractmethod

class Transformer(ABC):

    plugin_name = None
    plugin_category = "transformer"

    @abstractmethod
    def mutate(self, raw_data):
        """
        Transform a single value.

        Return:
            transformed value OR None to drop it
        """
        pass