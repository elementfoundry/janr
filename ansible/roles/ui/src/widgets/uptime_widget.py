from textual.widgets import Static
from textual.reactive import reactive
import psutil
import time


class UptimeWidget(Static):
    uptime = reactive("")

    def on_mount(self) -> None:
        self.set_interval(1, self.update_uptime)
        self.update_uptime()

    def update_uptime(self) -> None:
        boot = psutil.boot_time()
        elapsed = int(time.time() - boot)

        d, r = divmod(elapsed, 86400)
        h, r = divmod(r, 3600)
        m, s = divmod(r, 60)

        self.uptime = (
            f"{d}d {h:02}:{m:02}:{s:02}"
            if d
            else f"{h:02}:{m:02}:{s:02}"
        )

    def watch_uptime(self, uptime: str) -> None:
        self.update(uptime)
        