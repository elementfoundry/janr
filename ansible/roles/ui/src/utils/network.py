import time, os, subprocess, re

# =========================================================
# DHCP LAYER
# =========================================================

def parse_dhcp_leases() -> dict:
    path = "/var/lib/misc/dnsmasq.leases"
    leases = {}

    if not os.path.exists(path):
        return leases

    now = int(time.time())

    try:
        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue

                expiry = int(parts[0])
                mac = parts[1].lower()
                ip = parts[2]
                name = parts[3] if parts[3] != "*" else "unknown"

                leases[mac] = {
                    "ip": ip,
                    "name": name,
                    "lease_left": expiry - now,
                }

    except Exception:
        pass

    return leases


def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "expired"

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d:
        return f"{d}d {h:02}:{m:02}:{s:02}"
    if h:
        return f"{h:02}:{m:02}:{s:02}"
    return f"{m:02}:{s:02}"


# =========================================================
# HOSTAPD LAYER (FIXED)
# =========================================================

MAC_RE = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")


def get_hostapd_interfaces() -> list[str]:
    try:
        out = subprocess.run(
            ["/usr/sbin/hostapd_cli", "interface"],
            capture_output=True,
            text=True,
        )

        interfaces = []
        for line in out.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("Selected") or line.startswith("Available"):
                continue
            interfaces.append(line)

        return interfaces

    except Exception:
        return []


def parse_hostapd() -> dict:
    aps = {}

    for iface in get_hostapd_interfaces():
        try:
            out = subprocess.run(
                ["/usr/sbin/hostapd_cli", "-i", iface, "all_sta"],
                capture_output=True,
                text=True,
            )

            clients = []
            current = None

            for line in out.stdout.splitlines():
                line = line.strip().lower()

                # new client block starts with MAC
                if MAC_RE.match(line):
                    current = {
                        "mac": line,
                        "rx": 0,
                        "tx": 0,
                        "uptime": 0,
                    }
                    clients.append(current)
                    continue

                if current is None:
                    continue

                if line.startswith("rx_bytes="):
                    current["rx"] = int(line.split("=", 1)[1])
                elif line.startswith("tx_bytes="):
                    current["tx"] = int(line.split("=", 1)[1])
                elif line.startswith("connected_time="):
                    current["uptime"] = int(line.split("=", 1)[1])

            aps[iface] = clients

        except Exception:
            continue

    return aps


# =========================================================
# MODEL MERGE
# =========================================================

def build_client_model() -> dict:
    leases = parse_dhcp_leases()
    aps = parse_hostapd()

    model = {}

    for ap, clients in aps.items():
        rows = []

        for c in clients:
            lease = leases.get(c["mac"])

            rows.append({
                "endpoint": ap,
                "name": lease["name"] if lease else "unknown",
                "mac": c["mac"],
                "ip": lease["ip"] if lease else "-",
                "lease_left": format_duration(lease["lease_left"]) if lease else "-",
                "rx": c["rx"],
                "tx": c["tx"],
                "uptime": c["uptime"],
            })

        model[ap] = rows

    return model
