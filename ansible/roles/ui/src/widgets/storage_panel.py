import psutil
from textual.widgets import DataTable

def bytes_human(n):
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

class StoragePanel(DataTable):

    def on_mount(self):
        self.border_title = "STORAGE"
        self.cursor_type = "none"
        self.add_columns(
            "Mount",
            "Used",
            "Total",
            "%"
        )

        self.set_interval(10, self.refresh_storage)
        self.refresh_storage()

    def refresh_storage(self):
        self.clear()
        for part in psutil.disk_partitions(all=False):
            if part.fstype in ("tmpfs", "overlay", "squashfs"):
                continue

            try:
                usage = psutil.disk_usage(part.mountpoint)
                self.add_row(
                    part.mountpoint,
                    bytes_human(usage.used),
                    bytes_human(usage.total),
                    f"{usage.percent:.0f}%"
                )
            except Exception:
                pass