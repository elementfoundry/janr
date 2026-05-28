import re
from .base import Transformer


DOMAIN_REGEX = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)

IPV4_REGEX = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

class FinalizeDomainTransformerPlugin(Transformer):

    plugin_name = "finalize_domain"

    def mutate(self, raw_data):

        if raw_data is None:
            return None

        if not isinstance(raw_data, str):
            return None

        domain = raw_data.strip().lower().rstrip(".")

        if not domain:
            return None

        if IPV4_REGEX.match(domain):
            return None

        if not DOMAIN_REGEX.match(domain):
            return None

        return domain