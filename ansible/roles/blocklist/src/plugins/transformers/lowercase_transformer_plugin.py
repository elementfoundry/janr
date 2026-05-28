from .base import Transformer

class LowercaseTransformerPlugin(Transformer):

    plugin_name = "lowercase"

    def mutate(self, raw_data):
        """
        Converts raw_data to lowercase
        """

        if raw_data is None:
            return None
        cleaned = raw_data.lower()
        if not cleaned:
            return None
        return cleaned