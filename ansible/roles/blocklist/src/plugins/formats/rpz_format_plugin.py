from .base import Format

class RPZFormatPlugin(Format):

    plugin_name = "rpz"

    def mutate(self, raw_data):
        """
        RPZ format:
        - newline-delimited text
        - CNAME records assumed to be blocklist entries
        - no mutation needed at this level, handled by RPZExtractDomainTransformerPlugin after nomalization.
        """

        if not raw_data:
            return []

        for line in raw_data.splitlines():
            yield line
