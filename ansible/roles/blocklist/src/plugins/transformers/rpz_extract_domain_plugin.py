from .base import Transformer

class RpzExtractDomainTransformerPlugin(Transformer):

  plugin_name = "rpz_extract_domain"

  def mutate(self, raw_data):
      """
      Extract domain from RPZ CNAME rule.

      Example input:
          example.com CNAME .

      Output:
          example.com

      Non-domain records are ignored.
      """

      if raw_data is None:
          return None

      if not isinstance(raw_data, str):
          return None

      line = raw_data.strip()

      if not line:
          return None

      # skip comments
      if line.startswith(";"):
          return None

      # skip directives / zone metadata
      if (
          line.startswith("$")
          or " SOA " in line
          or " NS " in line
      ):
          return None

      parts = line.split()

      # expected:
      # domain CNAME .
      if len(parts) < 3:
          return None

      domain = parts[0]
      record_type = parts[1]
      target = parts[2]

      if record_type.upper() != "CNAME":
          return None

      if target != ".":
          return None

      # skip URLHaus test entry
      if domain == "testentry.rpz.urlhaus.abuse.ch":
          return None

      return domain