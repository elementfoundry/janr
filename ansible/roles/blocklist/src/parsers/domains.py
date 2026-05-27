# parsers/domains.py

from .base import Parser


class DomainsParser(Parser):
    format_name = "domains"

    def parse(self, lines):

        domains = set()

        for line in lines:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            domain = line.lower().rstrip(".")

            if " " in domain:
                continue

            domains.add(domain)

        return domains