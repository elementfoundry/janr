from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from utils.network import add_reserved_ip

class AddReservedIpDialog(ModalScreen):

    #TODO: move css to our dashboard.css file
    CSS = """
    AddReservedIpDialog {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: auto;

        padding: 1 2;

        border: round #ffcc66;
        background: #1a1a1a;
    }

    #dialog-title {
        width: 100%;
        content-align: center middle;

        margin-bottom: 1;

        color: #ffcc66;
        text-style: bold;
    }

    .dialog-label {
        margin-top: 1;
    }

    Input {
        width: 100%;
    }

    #button-bar {
        width: 100%;
        height: auto;

        margin-top: 2;

        align-horizontal: right;
    }

    Button {
        margin-left: 1;
    }
    """

    def compose(self) -> ComposeResult:

        with Vertical(id="dialog"):
            yield Label("ADD RESERVED IP", id="dialog-title")
            yield Label("MAC Address", classes="dialog-label")

            self.mac_input = Input(placeholder="aa:bb:cc:dd:ee:ff", id="mac")
            yield self.mac_input

            yield Label("Hostname", classes="dialog-label")
            self.hostname_input = Input(placeholder="printer", id="hostname")
            yield self.hostname_input

            yield Label("IP Address", classes="dialog-label")
            self.ip_input = Input(placeholder="10.10.0.x", id="ip")
            yield self.ip_input

            with Horizontal(id="button-bar"):
                yield Button("Cancel", id="cancel")
                yield Button("Apply", id="apply", variant="success")

    # =====================================================
    # HELPERS
    # =====================================================

    def dismiss_cancel(self):
        self.dismiss(None)

    def dismiss_success(self):
        mac = self.mac_input.value.strip()
        hostname = self.hostname_input.value.strip()
        ip = self.ip_input.value.strip()

        success, message = add_reserved_ip(mac, hostname, ip)

        if not success:
            self.notify(message, severity="error")
            return

        self.dismiss({
            "mac": mac,
            "hostname": hostname,
            "fqdn": f"{hostname}.janr",
            "ip": ip
        })

    # =====================================================
    # EVENTS
    # =====================================================

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id

        if button_id == "cancel":
            self.dismiss_cancel()
            return

        if button_id == "apply":
            self.dismiss_success()
            return

    def on_input_submitted(self, event: Input.Submitted):
        self.dismiss_success()