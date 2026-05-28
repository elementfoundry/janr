from .base import Format

class PlaintextFormatPlugin(Format):

    plugin_name = "plaintext"

    def mutate(self, raw_data):
        """
        Plaintext format:
        - newline-delimited text
        - no structure assumed
        """

        if not raw_data:
            return []

        for line in raw_data.splitlines():
            yield line
