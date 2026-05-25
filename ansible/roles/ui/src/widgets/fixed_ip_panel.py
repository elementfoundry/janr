from textual.widgets import DataTable
from utils.network import parse_fixed_ips

class FixedIpPanel(DataTable):

    def on_mount(self):
        self.cursor_type = "none"

        self.add_columns(
            "Hostname",
            "FQDN",
            "MAC",
            "IP",
        )
        self.refresh_leases()

    def refresh_leases(self):
        self.clear()

        leases = parse_fixed_ips()

        if not leases:
            self.add_row("--- no static leases configured ---")
            return

        for lease in leases:
            self.add_row(
                lease["hostname"],
                lease["fqdn"],
                lease["mac"],
                lease["ip"],
            )