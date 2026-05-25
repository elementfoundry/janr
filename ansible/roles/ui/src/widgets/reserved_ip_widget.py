from textual.containers import Container, Horizontal
from textual.widgets import DataTable, Button, Static
from utils.network import parse_reserved_ips, remove_reserved_ip

from widgets.dialogs.add_reserved_ip_dialog import AddReservedIpDialog
from widgets.dialogs.confirm_delete_reserved_ip import ConfirmDeleteReservedIpDialog


class ReservedIpWidget(Static):

    def compose(self):
        self.table = DataTable(cursor_type="row")
        self.table.add_columns("Hostname", "FQDN", "MAC", "IP")
        yield self.table

        with Horizontal(id="reserved-ip-buttons"):
            yield Button("Add", id="reserved-add", variant="success")
            yield Button("Remove", id="reserved-remove", variant="error")

    def on_mount(self):
        self.border_title = "RESERVED IPS"
        self.refresh_table()

    def refresh_table(self):
        self.table.clear(columns=False)
        entries = parse_reserved_ips()
        if not entries:
            self.table.add_row("--- no reserved ips configured ---")
            return

        for e in entries:
            self.table.add_row(e["hostname"], e["fqdn"], e["mac"] or "-", e["ip"])

        # reset cursor to top
        self.table.cursor_coordinate = (0, 0)
        
    def get_selected_entry(self):
        if self.table.row_count == 0:
            return None

        try:
            row = self.table.get_row_at(self.table.cursor_row)
            hostname = row[0]
            for e in parse_reserved_ips():
                if e["hostname"] == hostname:
                    return e

        except Exception:
            return None

        return None

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id

        if bid == "reserved-add":
            def after_add(result):
                if not result:
                    return
                self.refresh_table()

            self.app.push_screen(AddReservedIpDialog(), after_add)
            return

        if bid == "reserved-remove":
            entry = self.get_selected_entry()
            if not entry:
                self.app.notify("No reserved IP selected", severity="warning")
                return

            def after_confirm(confirmed: bool):
                if not confirmed:
                    return

                success = remove_reserved_ip(entry["mac"])
                if success:
                    self.app.notify(f"Removed {entry['hostname']}", severity="information")
                    self.refresh_table()
                else:
                    self.app.notify("Failed to remove reserved IP", severity="error")

            self.app.push_screen(ConfirmDeleteReservedIpDialog(entry), after_confirm)