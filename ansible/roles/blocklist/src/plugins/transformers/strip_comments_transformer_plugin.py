from .base import Transformer

COMMENT_PREFIXES = ("#", ";")

class StripCommentsTransformerPlugin(Transformer):

    plugin_name = "strip_comments"

    def mutate(self, raw_data):
        """
        Removes inline and full-line comments from a record.

        Supports:
        - '#' style comments
        - ';' style comments

        Preserves content before the first comment marker.
        """

        if raw_data is None:
            return None

        cleaned = raw_data

        # Find earliest comment marker
        positions = [
            cleaned.find(prefix)
            for prefix in COMMENT_PREFIXES
            if prefix in cleaned
        ]
        if positions:
            cleaned = cleaned[:min(positions)]
        cleaned = cleaned.strip()
        if not cleaned:
            return None

        return cleaned