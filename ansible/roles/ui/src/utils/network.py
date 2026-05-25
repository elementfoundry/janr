import time, os, subprocess, re, hashlib

# =========================================================
# PATHS
# =========================================================

DNSMASQ_LEASE_PATH = "/var/lib/misc/dnsmasq.leases"
DNSMASQ_FIXED_PATH = "/etc/dnsmasq.d/janr-dnsmasq-fixed-ips.conf"
DNSMASQ_RESERVED_PATH = "/etc/dnsmasq.d/janr-dnsmasq-reserved-ips.conf"
UNBOUND_RESERVED_PATH = "/etc/unbound/unbound.conf.d/janr-unbound-reserved-ips.conf"
UNBOUND_FIXED_PATH = "/etc/unbound/unbound.conf.d/janr-unbound-fixed-ips.conf"

# =========================================================
# REGEX
# =========================================================

MAC_RE = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")
LOCAL_DATA_RE = re.compile(r'local-data:\s*"([^\.]+)\.home\.arpa\.\s+IN\s+A\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"')
LOCAL_PTR_RE = re.compile(r'local-data-ptr:\s*"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+([^.]+)\.home\.arpa"')
RID_RE = re.compile(r"#\s*janr:([a-f0-9]+)")

# =========================================================
# HELPERS
# =========================================================

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


def restart_services():
    os.system("sudo systemctl restart janr-unbound")
    os.system("sudo systemctl restart janr-dnsmasq")


def generate_reservation_id(mac: str, hostname: str, ip: str) -> str:

    raw = (
        f"{mac.lower()}:"
        f"{hostname.lower()}:"
        f"{ip}"
    )

    return hashlib.sha256(raw.encode()).hexdigest()[:8]


# =========================================================
# DHCP LEASES
# =========================================================

def parse_dhcp_leases() -> dict:

    leases = {}

    if not os.path.exists(DNSMASQ_LEASE_PATH):
        return leases

    now = int(time.time())

    try:
        with open(DNSMASQ_LEASE_PATH, "r") as f:
            for line in f:
                parts = line.strip().split()

                if len(parts) < 4:
                    continue

                expiry = int(parts[0])
                mac = parts[1].lower()
                ip = parts[2]
                name = (
                    parts[3]
                    if parts[3] != "*"
                    else "unknown"
                )

                leases[mac] = {
                    "ip": ip,
                    "name": name,
                    "lease_left": (
                        expiry - now
                    ),
                }

    except Exception:
        pass

    return leases


# =========================================================
# HOSTAPD
# =========================================================

def get_hostapd_interfaces() -> list[str]:
    try:
        out = subprocess.run(
            [
                "/usr/sbin/hostapd_cli",
                "interface",
            ],
            capture_output=True,
            text=True,
        )

        interfaces = []

        for line in out.stdout.splitlines():

            line = line.strip()

            if (
                not line
                or line.startswith("Selected")
                or line.startswith("Available")
            ):
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
                [
                    "/usr/sbin/hostapd_cli",
                    "-i",
                    iface,
                    "all_sta",
                ],
                capture_output=True,
                text=True,
            )

            clients = []

            current = None

            for line in out.stdout.splitlines():

                line = (
                    line
                    .strip()
                    .lower()
                )

                # -----------------------------
                # NEW CLIENT
                # -----------------------------

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

                # -----------------------------
                # FIELDS
                # -----------------------------

                if line.startswith("rx_bytes="):

                    current["rx"] = int(
                        line.split("=", 1)[1]
                    )

                elif line.startswith("tx_bytes="):

                    current["tx"] = int(
                        line.split("=", 1)[1]
                    )

                elif line.startswith(
                    "connected_time="
                ):

                    current["uptime"] = int(
                        line.split("=", 1)[1]
                    )

            aps[iface] = clients

        except Exception:
            continue

    return aps


# =========================================================
# CLIENT MODEL
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

                "name": (
                    lease["name"]
                    if lease
                    else "unknown"
                ),

                "mac": c["mac"],

                "ip": (
                    lease["ip"]
                    if lease
                    else "-"
                ),

                "lease_left": (
                    format_duration(
                        lease["lease_left"]
                    )
                    if lease
                    else "-"
                ),

                "rx": c["rx"],

                "tx": c["tx"],

                "uptime": c["uptime"],
            })

        model[ap] = rows

    return model


# =========================================================
# FIXED IPS
# =========================================================
def parse_unbound_fqdns() -> dict[str, str]:
    """
    Returns:
        {
            "10.10.0.13": "minon.home.arpa",
            ...
        }
    """

    entries = {}

    if not os.path.exists(UNBOUND_FIXED_PATH):
        return entries

    pattern = re.compile(r'local-data:\s+"([^"]+)\.\s+IN\s+A\s+([0-9.]+)"')

    try:
        with open(UNBOUND_FIXED_PATH, "r") as f:
            for line in f:
                line = line.strip()

                match = pattern.search(line)
                if not match:
                    continue

                fqdn = match.group(1)
                ip = match.group(2)

                entries[ip] = fqdn

    except Exception:
        pass

    return entries

def parse_fixed_ips() -> list[dict]:

    entries = []

    if not os.path.exists(DNSMASQ_FIXED_PATH):
        return entries

    unbound_fqdns = parse_unbound_fqdns()

    try:
        with open(DNSMASQ_FIXED_PATH, "r") as f:
            for line in f:
                line = line.strip()

                if not line.startswith("dhcp-host="):
                    continue

                line = line.split("#")[0].strip()

                parts = (line.replace("dhcp-host=", "").split(","))

                if len(parts) < 3:
                    continue

                mac = parts[0].lower()
                hostname = parts[1]
                ip = parts[2]

                entries.append({
                    "mac": mac,
                    "hostname": hostname,
                    "fqdn": unbound_fqdns.get(ip, hostname),
                    "ip": ip,
                })

    except Exception:
        pass

    return entries
# def parse_fixed_ips() -> list[dict]:

#     entries = []

#     if not os.path.exists(DNSMASQ_FIXED_PATH):
#         return entries

#     try:
#         with open(DNSMASQ_FIXED_PATH, "r") as f:
#             for line in f:
#                 line = line.strip()
#                 if not line.startswith("dhcp-host="):
#                     continue
#                 line = line.split("#")[0].strip()
#                 parts = (line.replace("dhcp-host=", "").split(","))

#                 if len(parts) < 3:
#                     continue

#                 mac = parts[0].lower()
#                 hostname = parts[1]
#                 ip = parts[2]

#                 entries.append({
#                     "mac": mac,
#                     "hostname": hostname,
#                     "fqdn": (
#                         f"{hostname}.home.arpa"
#                     ),
#                     "ip": ip,
#                 })

#     except Exception:
#         pass

#     return entries


# =========================================================
# RESERVED IPS
# =========================================================

def parse_reserved_ips() -> list[dict]:

    entries = {}

    # =====================================================
    # UNBOUND
    # =====================================================

    if os.path.exists(
        UNBOUND_RESERVED_PATH
    ):

        try:

            with open(
                UNBOUND_RESERVED_PATH,
                "r",
            ) as f:

                for line in f:

                    line = line.strip()

                    # -------------------------
                    # local-data
                    # -------------------------

                    m = LOCAL_DATA_RE.search(
                        line
                    )

                    if m:

                        hostname = m.group(1)

                        ip = m.group(2)

                        rid_match = (
                            RID_RE.search(line)
                        )

                        rid = (
                            rid_match.group(1)
                            if rid_match
                            else None
                        )

                        entries[ip] = {

                            "hostname": hostname,

                            "fqdn": (
                                f"{hostname}.home.arpa"
                            ),

                            "ip": ip,

                            "mac": None,

                            "rid": rid,
                        }

        except Exception:
            pass

    # =====================================================
    # DNSMASQ ENRICHMENT
    # =====================================================

    if os.path.exists(
        DNSMASQ_RESERVED_PATH
    ):

        try:

            with open(
                DNSMASQ_RESERVED_PATH,
                "r",
            ) as f:

                for line in f:

                    line = line.strip()

                    if not line.startswith(
                        "dhcp-host="
                    ):
                        continue

                    clean = line.split(
                        "#",
                        1
                    )[0].strip()

                    parts = (
                        clean
                        .replace(
                            "dhcp-host=",
                            ""
                        )
                        .split(",")
                    )

                    if len(parts) < 3:
                        continue

                    mac = (
                        parts[0]
                        .lower()
                    )

                    hostname = parts[1]

                    ip = parts[2]

                    if ip in entries:

                        entries[ip]["mac"] = mac

                        entries[ip][
                            "hostname"
                        ] = hostname

        except Exception:
            pass

    return list(entries.values())


# =========================================================
# RESERVED IP ADD
# =========================================================

def add_reserved_ip(
    mac: str,
    hostname: str,
    ip: str,
):

    mac = mac.lower()

    # =====================================================
    # DUPLICATE CHECKS
    # =====================================================

    for entry in parse_fixed_ips():

        if entry["mac"] == mac:
            return (
                False,
                "MAC already exists "
                "in fixed IPs",
            )

        if entry["hostname"] == hostname:
            return (
                False,
                "Hostname already exists "
                "in fixed IPs",
            )

        if entry["ip"] == ip:
            return (
                False,
                "IP already exists "
                "in fixed IPs",
            )

    for entry in parse_reserved_ips():

        if entry["mac"] == mac:
            return (
                False,
                "MAC already reserved",
            )

        if entry["hostname"] == hostname:
            return (
                False,
                "Hostname already reserved",
            )

        if entry["ip"] == ip:
            return (
                False,
                "IP already reserved",
            )

    # =====================================================
    # WRITE
    # =====================================================

    fqdn = f"{hostname}.home.arpa."

    rid = generate_reservation_id(
        mac,
        hostname,
        ip,
    )

    try:

        # -------------------------------------------------
        # UNBOUND
        # -------------------------------------------------

        with open(
            UNBOUND_RESERVED_PATH,
            "a",
        ) as f:

            f.write(
                f'\n  local-data: '
                f'"{fqdn} IN A {ip}" '
                f'# janr:{rid}\n'
            )

            f.write(
                f'  local-data-ptr: '
                f'"{ip} {hostname}.home.arpa" '
                f'# janr:{rid}'
            )

        # -------------------------------------------------
        # DNSMASQ
        # -------------------------------------------------

        with open(
            DNSMASQ_RESERVED_PATH,
            "a",
        ) as f:

            f.write(
                f"\ndhcp-host="
                f"{mac},{hostname},{ip} "
                f"# janr:{rid}"
            )

        restart_services()

        return True, "ok"

    except Exception as e:

        return False, str(e)


# =========================================================
# RESERVED IP REMOVE
# =========================================================

def remove_reserved_ip(
    mac: str,
) -> bool:

    mac = mac.lower()

    hostname = None
    ip = None
    rid = None

    # =====================================================
    # FIND ENTRY
    # =====================================================

    for entry in parse_reserved_ips():

        if entry["mac"] == mac:

            hostname = entry["hostname"]

            ip = entry["ip"]

            rid = entry["rid"]

            break

    if not rid:
        return False

    try:

        # =================================================
        # DNSMASQ
        # =================================================

        if os.path.exists(
            DNSMASQ_RESERVED_PATH
        ):

            with open(
                DNSMASQ_RESERVED_PATH,
                "r",
            ) as f:

                lines = f.readlines()

            with open(
                DNSMASQ_RESERVED_PATH,
                "w",
            ) as f:

                for line in lines:

                    if (
                        f"# janr:{rid}"
                        in line
                    ):
                        continue

                    f.write(line)

        # =================================================
        # UNBOUND
        # =================================================

        if os.path.exists(
            UNBOUND_RESERVED_PATH
        ):

            with open(
                UNBOUND_RESERVED_PATH,
                "r",
            ) as f:

                lines = f.readlines()

            with open(
                UNBOUND_RESERVED_PATH,
                "w",
            ) as f:

                for line in lines:

                    if (
                        f"# janr:{rid}"
                        in line
                    ):
                        continue

                    f.write(line)

        restart_services()

        return True

    except Exception as e:

        print(
            f"[remove_reserved_ip] {e}"
        )

        return False