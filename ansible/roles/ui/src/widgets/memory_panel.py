import psutil
from textual.widgets import Static
from textual.reactive import reactive

def bytes_human(n):
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

class MemoryPanel(Static):
    content = reactive("")
    def on_mount(self):
        self.border_title = "MEMORY"
        self.set_interval(2, self.refresh_stats)
        self.refresh_stats()

    def refresh_stats(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        lines = []

        lines.append(
            f"Memory Used\n"
            f"{bytes_human(mem.used)} / {bytes_human(mem.total)}"
        )
        
        lines.append("")

        lines.append(
            f"Virtual Memory\n"
            f"{bytes_human(swap.used)} / {bytes_human(swap.total)}"
        )
        self.content = "\n".join(lines)

    def watch_content(self, value):
        self.update(value)