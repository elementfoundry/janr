from textual.widgets import DataTable, Static
from utils.network import build_client_model

class ClientsView(Static):

    def on_mount(self) -> None:

        self.tables: dict[str, DataTable] = {}
        self.empty_messages: dict[str, Static] = {}
        self.headers: dict[str, Static] = {}

        # endpoint -> row cache
        self.rows: dict[str, dict[str, dict]] = {}

        self.set_interval(3, self.refresh_clients)
        self.refresh_clients()

    def refresh_clients(self) -> None:

        model = build_client_model()

        # remove endpoints that disappeared
        for endpoint in list(self.tables):
            if endpoint not in model:
                try:
                    self.headers[endpoint].remove()
                    self.tables[endpoint].remove()

                    if endpoint in self.empty_messages:
                        self.empty_messages[endpoint].remove()

                except Exception:
                    pass

                del self.tables[endpoint]
                del self.headers[endpoint]
                self.rows.pop(endpoint, None)

                if endpoint in self.empty_messages:
                    del self.empty_messages[endpoint]

        # create / update endpoints
        for endpoint, clients in model.items():
            # create endpoint section if needed
            if endpoint not in self.tables:

                header = Static(f"[b]{endpoint}[/b]")
                self.mount(header)

                table = DataTable(cursor_type="none")
                table.zebra_stripes = False

                # IMPORTANT: use column KEYS for update_cell safety
                table.add_column("Name", key="name", width=18)
                table.add_column("MAC", key="mac", width=17)
                table.add_column("IP", key="ip", width=15)
                table.add_column("Lease Left", key="lease", width=12)
                table.add_column("RX", key="rx", width=12)
                table.add_column("TX", key="tx", width=12)
                table.add_column("Uptime", key="uptime", width=10)

                self.mount(table)

                empty = Static(
                    "[dim]---No current clients detected---[/dim]"
                )
                self.mount(empty)
                self.mount(Static(""))  # spacer
                self.headers[endpoint] = header
                self.tables[endpoint] = table
                self.empty_messages[endpoint] = empty
                self.rows[endpoint] = {}

            table = self.tables[endpoint]
            empty = self.empty_messages[endpoint]

            # toggle empty state
            if not clients:
                table.display = False
                empty.display = True
                continue
            else:
                table.display = True
                empty.display = False

            current_rows: dict[str, dict] = {}

            # normalize clients
            for client in clients:
                mac = client.get("mac", "").lower()
                if not mac:
                    continue

                current_rows[mac] = {
                    "name": client.get("name", "unknown"),
                    "mac": mac,
                    "ip": client.get("ip", ""),
                    "lease_left": client.get("lease_left", "-"),
                    "rx": str(client.get("rx", 0)),
                    "tx": str(client.get("tx", 0)),
                    "uptime": str(client.get("uptime", 0)),
                }

            # remove disconnected rows
            for mac in list(self.rows[endpoint]):
                if mac not in current_rows:
                    try:
                        table.remove_row(mac)
                    except Exception:
                        pass
                    del self.rows[endpoint][mac]

            # add/update rows
            for mac, row in current_rows.items():
                # new row
                if mac not in self.rows[endpoint]:
                    table.add_row(
                        row["name"],
                        row["mac"],
                        row["ip"],
                        row["lease_left"],
                        row["rx"],
                        row["tx"],
                        row["uptime"],
                        key=mac,
                    )

                    self.rows[endpoint][mac] = row
                    continue

                # update changed cells only
                old = self.rows[endpoint][mac]

                updates = [
                    ("name", "name"),
                    ("mac", "mac"),
                    ("ip", "ip"),
                    ("lease", "lease_left"),
                    ("rx", "rx"),
                    ("tx", "tx"),
                    ("uptime", "uptime"),
                ]

                for col_key, field in updates:
                    if old[field] != row[field]:
                        try:
                            table.update_cell(
                                mac,
                                col_key,
                                row[field],
                            )
                        except Exception:
                            pass

                self.rows[endpoint][mac] = row