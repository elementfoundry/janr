import re
from .base import Parser


DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9-]+\.)+[a-z]{2,}$"
)


class HostsParser(Parser):
    format_name = "hosts"

    def parse(self, lines):
        domains = set()

        for line in lines:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            # Must be at least: IP + domain
            if len(parts) < 2:
                continue

            ip = parts[0]

            # only accept standard hosts sink formats
            if ip not in ("0.0.0.0", "127.0.0.1"):
                continue

            domain = parts[1].strip().lower().rstrip(".")

            # -------------------------------------------------
            # HARD FILTER 1: reject obvious malformed prefixes
            # -------------------------------------------------
            if domain.startswith("0.0.0.0"):
                continue

            if domain.startswith(ip + "."):
                continue

            # -------------------------------------------------
            # HARD FILTER 2: must contain at least one dot
            # -------------------------------------------------
            if "." not in domain:
                continue

            # -------------------------------------------------
            # HARD FILTER 3: RFC-like validation
            # -------------------------------------------------
            if not DOMAIN_RE.match(domain):
                continue

            # -------------------------------------------------
            # extra safety exclusions
            # -------------------------------------------------
            if domain in ("localhost", "localhost.localdomain"):
                continue

            domains.add(domain)

        return domains