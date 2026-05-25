from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Button
from utils.network import remove_reserved_ip

class ConfirmDeleteReservedIpDialog(ModalScreen):

    #TODO: move css to our dashboard.css file
    CSS = """
    ConfirmDeleteReservedIpDialog {
        align: center middle;
    }

    #dialog {
        width: 70;
        height: auto;

        padding: 1 2;

        border: round #ffcc66;
        background: #1a1a1a;
    }

    #title {
        width: 100%;
        content-align: center middle;

        margin-bottom: 1;

        color: #ff6666;
        text-style: bold;
    }

    #details {
        margin-top: 1;
        margin-bottom: 2;
    }

    #button-bar {
        width: 100%;
        height: auto;

        align-horizontal: right;
    }

    Button {
        margin-left: 1;
    }
    """

    def __init__(self, entry: dict):
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        e = self.entry
        with Vertical(id="dialog"):
            
            yield Label("CONFIRM DELETE RESERVED IP",id="title")
            yield Label("You are about to remove:")
            yield Label(f"Hostname: {e['hostname']}", id="details")
            yield Label(f"FQDN: {e['fqdn']}")
            yield Label(f"MAC: {e['mac']}")
            yield Label(f"IP: {e['ip']}")

            with Horizontal(id="button-bar"):
                yield Button("Cancel", id="cancel")
                yield Button("Delete", id="delete", variant="error")

    # =====================================================
    # EVENTS
    # =====================================================

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.dismiss(False)
            return

        if event.button.id == "delete":
            self.dismiss(True)