from .base import Transformer

class TrimTransformerPlugin(Transformer):

    plugin_name = "trim"

    def mutate(self, raw_data):
        """
        Trims leading and trailing whitespace from a record.
        """

        if raw_data is None:
            return None
        cleaned = raw_data.strip()
        if not cleaned:
            return None
        return cleaned