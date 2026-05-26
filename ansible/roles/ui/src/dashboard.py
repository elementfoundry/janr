#!/usr/bin/env python3

import getpass, platform, os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import Footer, Static, TabbedContent, TabPane, DataTable, RichLog, Button
from widgets.uptime_widget import UptimeWidget
from widgets.cpu_panel import CpuPanel
from widgets.memory_panel import MemoryPanel
from widgets.endpoint_panel import EndpointPanel
from widgets.storage_panel import StoragePanel
from widgets.fixed_ip_panel import FixedIpPanel
from widgets.reserved_ip_widget import ReservedIpWidget
from widgets.htp import HackThePlanet
from views.clients_view import ClientsView
from utils.network import *

JANR_VERSION = "v0.1a"

class HeaderBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static(f"{getpass.getuser()} :: {platform.node()}", id="header-left")
        yield UptimeWidget(id="header-center")
        yield Static(f"JANR {JANR_VERSION}", id="header-right")

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
                with VerticalScroll():
                    with Container(id="clients-container", classes="panel") as panel:
                        panel.border_title = "ENDPOINT CLIENTS"
                        yield ClientsView()
                    with Container(id="fixed-ips", classes="panel") as panel:
                        panel.border_title = "FIXED IPS"
                        yield FixedIpPanel()
                    with Container(id="reserved-ips", classes="panel") as panel:
                        panel.border_title = "RESERVED IPS"
                        yield ReservedIpWidget()
                        
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