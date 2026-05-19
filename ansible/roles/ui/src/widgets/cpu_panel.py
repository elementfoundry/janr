import psutil
from textual.widgets import Static
from textual.reactive import reactive


class CpuPanel(Static):

    content = reactive("")

    def __init__(self):
        super().__init__(markup=False)

    def on_mount(self):
        self.border_title = "SYSTEM"
        self.set_interval(1, self.refresh_stats)
        self.refresh_stats()

    def refresh_stats(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        freq = psutil.cpu_freq()
        ghz = 0.0

        if freq:
            ghz = freq.current / 1000

        temp = "N/A"

        try:
            temps = psutil.sensors_temperatures()
            for _, entries in temps.items():
                if entries:
                    temp = f"{entries[0].current:.1f}°C"
                    break
        except Exception:
            pass

        lines = []

        lines.append(f"CPU Temp    {temp}")
        lines.append(f"CPU Speed   {ghz:.2f} GHz")
        lines.append(f"CPU Usage   {cpu_usage:.1f}%")
        lines.append("")

        for idx, usage in enumerate(per_core):
            bars = "█" * int(usage / 10)
            bars = bars.ljust(10, "░")
            lines.append(
                f"CPU{idx:<2} [{bars}] {usage:>5.1f}%"
            )
        self.content = "\n".join(lines)

    def watch_content(self, value):
      self.update(value)