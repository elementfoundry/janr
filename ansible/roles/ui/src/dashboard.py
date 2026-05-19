#!/usr/bin/env python3

import getpass, platform, os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import Footer, Static, TabbedContent, TabPane, DataTable, RichLog

from widgets.uptime_widget import UptimeWidget
from widgets.cpu_panel import CpuPanel
from widgets.memory_panel import MemoryPanel
from widgets.endpoint_panel import EndpointPanel
from widgets.storage_panel import StoragePanel
from widgets.htp import HackThePlanet
from utils.network import *

JANR_VERSION = "v0.1a"

class HeaderBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static(f"{getpass.getuser()} :: {platform.node()}", id="header-left")
        yield UptimeWidget(id="header-center")
        yield Static(f"JANR {JANR_VERSION}", id="header-right")


# =========================================================
# CLIENT VIEW (ONE TABLE PER ENDPOINT)
# =========================================================

class ClientsView(Vertical):
    def on_mount(self) -> None:
        self.set_interval(3, self.refresh_clients)
        self.refresh_clients()

    def refresh_clients(self) -> None:
        model = build_client_model()

        self.remove_children()

        if not model:
            self.mount(Static("NO CLIENT DATA"))
            return

        for endpoint, clients in model.items():

            self.mount(Static(f"[b]{endpoint}[/b]"))

            table = DataTable(cursor_type="none")

            table.add_columns(
                "Name",
                "MAC",
                "IP",
                "Lease Left",
                "RX",
                "TX",
                "Uptime",
            )

            if not clients:
                table.add_row(
                    "--- no current clients detected ---",
                    "", "", "", "", "", ""
                )
            else:
                for c in clients:
                    table.add_row(
                        c.get("name", "unknown"),
                        c.get("mac", ""),
                        c.get("ip", ""),
                        c.get("lease_left", "-"),
                        str(c.get("rx", 0)),
                        str(c.get("tx", 0)),
                        str(c.get("uptime", 0)),
                    )

            self.mount(table)
            self.mount(Static(""))


# =========================================================
# LOG
# =========================================================

class LiveLog(RichLog):
    LOG_PATH = "/var/log/janr/firewall.log"

    def on_mount(self) -> None:
        self._file = None
        self.set_interval(0.5, self.poll)
        self.open_file()

    def open_file(self) -> None:
        if not os.path.exists(self.LOG_PATH):
            self.write("--- log missing ---")
            return

        self._file = open(self.LOG_PATH, "r", encoding="utf-8", errors="replace")
        self._file.seek(0, 2)

    def poll(self) -> None:
        if not self._file:
            return

        line = self._file.readline()
        if line:
            self.write(line.rstrip("\n"))


# =========================================================
# APP
# =========================================================

class DashboardApp(App[None]):
    CSS_PATH = "dashboard.css"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("left", "previous_tab", "Prev Tab"),
        Binding("right", "next_tab", "Next Tab"),
    ]

    def compose(self) -> ComposeResult:
        yield HeaderBar()

        with TabbedContent(initial="overview"):

            with TabPane("Overview", id="overview"):
                with Container(id="overview-grid"):

                    yield CpuPanel()
                    yield MemoryPanel()
                    yield EndpointPanel()
                    yield StoragePanel()

            with TabPane("Clients", id="clients"):
                yield ClientsView()

            with TabPane("Firewall Log", id="log"):
                yield LiveLog()


            with TabPane("About", id="about"):
                with Vertical():
                    with VerticalScroll():
                        yield Static(
                            """
Welcome to J.A.N.R. (Just Another Network Router). A project inspired by DasGeek and the Destination Linux team on episode 459. So Ryan, if you're reading this, you are responsible for the sleepless nights, hours of talking to myself, and almost unhealty obsession in building out this purpose built router stack. I have only these words for you...

Thanks man! It was fun! 

This was designed to run on minimal hardware (an orange pi zero 2w) with multiple access points. Not the networking beast you may have envisioned, but I wanted to challenge myself with something minimal.

P.S. - Michael AI was not used in the creation of this project. 
                            """     
                        )
                    with Container(id="about-footer"):
                        yield HackThePlanet()


        yield Footer()


if __name__ == "__main__":
    DashboardApp().run()