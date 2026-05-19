from textual.widgets import DataTable
from utils.network import build_client_model

class EndpointPanel(DataTable):

    def on_mount(self):
        self.border_title = "CLIENT ENDPOINTS"
        self.cursor_type = "none"
        self.add_columns(
            "Endpoint",
            "Clients"
        )
        self.set_interval(3, self.refresh_clients)
        self.refresh_clients()

    def refresh_clients(self):
        self.clear()
        model = build_client_model()
        total = 0
        for endpoint, clients in model.items():
            count = len(clients)
            total += count
            self.add_row(
                endpoint,
                str(count)
            )
        self.add_row("", "")
        self.add_row("TOTAL", str(total))