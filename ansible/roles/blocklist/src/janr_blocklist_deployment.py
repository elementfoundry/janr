#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import urllib.request

from janr_blocklists import BLOCKLISTS
from plugins.plugin_manager import PluginManager


BASE_DIR = pathlib.Path("/opt/janr/blocklist")

DOWNLOAD_DIR = BASE_DIR / "downloads"
RPZ_DIR = BASE_DIR / "rpz"
LOG_DIR = BASE_DIR / "logs"


# -----------------------------
# filesystem setup
# -----------------------------

def ensure_directories():
    for directory in (DOWNLOAD_DIR, RPZ_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


# -----------------------------
# downloading
# -----------------------------

def download_blocklist(blocklist):
    dest = DOWNLOAD_DIR / f"{blocklist.id}.txt"

    print(f"[janr] downloading {blocklist.name}")

    urllib.request.urlretrieve(blocklist.url, dest)

    return dest


# -----------------------------
# file loading
# -----------------------------

def load_lines(path: pathlib.Path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()


# -----------------------------
# pipeline
# -----------------------------

def run_pipeline(blocklist, lines):

    # -----------------------------
    # 1. format plugin
    # -----------------------------

    format_cls = PluginManager.format(blocklist.format)
    format_plugin = format_cls()

    records = format_plugin.mutate("\n".join(lines))

    if not records:
        return []

    # -----------------------------
    # 2. transformer chain
    # -----------------------------

    transformers = [
        PluginManager.transformer(name)()
        for name in getattr(blocklist, "transformers", [])
    ]

    output = []

    for record in records:

        value = record

        for transformer in transformers:
            value = transformer.mutate(value)

            if value is None:
                break

        if value is not None:
            output.append(value)

    return output


# -----------------------------
# RPZ generation
# -----------------------------

def write_rpz(blocklist, domains):

    rpz_path = RPZ_DIR / f"{blocklist.id}.rpz"

    print(
        f"[janr] generating RPZ for {blocklist.name} "
        f"({len(domains)} domains)"
    )

    with open(rpz_path, "w") as f:

        f.write("$TTL 2h\n")
        f.write(
            "@ IN SOA localhost. root.localhost. "
            "1 1h 15m 30d 2h\n"
        )
        f.write("  IN NS localhost.\n\n")

        for domain in sorted(domains):
            f.write(f"{domain} CNAME .\n")

    return rpz_path


# -----------------------------
# Unbound config generation
# -----------------------------

def write_unbound_config(blocklist, rpz_path):

    conf_path = pathlib.Path(
        f"/etc/unbound/unbound.conf.d/janr-{blocklist.id}.conf"
    )

    content = (
        "rpz:\n"
        f'  name: "{blocklist.id}"\n'
        f'  zonefile: "{rpz_path}"\n'
    )

    with open(conf_path, "w") as f:
        f.write(content)

    return conf_path


# -----------------------------
# deployment
# -----------------------------

def deploy_blocklist(blocklist):

    downloaded = download_blocklist(blocklist)
    lines = load_lines(downloaded)
    domains = run_pipeline(blocklist, lines)

    rpz_path = write_rpz(blocklist, domains)
    write_unbound_config(blocklist, rpz_path)


# -----------------------------
# unbound reload
# -----------------------------

def restart_unbound():

    print("[janr] restarting unbound")

    subprocess.run(
        ["systemctl", "restart", "janr-unbound"],
        check=True,
    )


# -----------------------------
# main
# -----------------------------

def main():

    # bootstrap plugins
    PluginManager.discover("plugins.formats")
    PluginManager.discover("plugins.transformers")

    ensure_directories()

    enabled = [b for b in BLOCKLISTS if b.enabled]

    if not enabled:
        print("[janr] no enabled blocklists")
        return

    for blocklist in enabled:
        try:
            deploy_blocklist(blocklist)

        except Exception as e:
            print(
                f"[janr] failed {blocklist.name}: {e}",
                file=sys.stderr,
            )

    restart_unbound()

    print("[janr] blocklist deployment complete")


if __name__ == "__main__":
    main()