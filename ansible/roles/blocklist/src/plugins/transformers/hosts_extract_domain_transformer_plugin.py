from .base import Transformer

class HostsExtractDomainTransformerPlugin(Transformer):

    plugin_name = "hosts_extract_domain"

    def mutate(self, raw_data):
        """
        Extracts domain from a hosts-formatted line.

        Expected input after earlier transformers:
        - "0.0.0.0 example.com"
        - "127.0.0.1 example.com"
        """

        if raw_data is None:
            return None
        # Split on whitespace
        parts = raw_data.split()
        # Must have at least:IP + domain
        if len(parts) < 2:
            return None
        domain = parts[1].strip()
        if not domain:
            return None
        return domain