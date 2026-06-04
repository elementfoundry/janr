#!/usr/bin/env python3

import pathlib
import subprocess
from pathlib import Path

from core.asset import Asset
from core.janr_logger import logger
from janr_blocklists import BLOCKLISTS
from plugins.plugin_manager import PluginManager

# -----------------------------
# paths
# -----------------------------

BASE_DIR = pathlib.Path("/opt/janr/blocklist")
DOWNLOAD_DIR = Path("/run/janr/blocklist/downloads")
RPZ_DIR = Path("/run/janr/blocklist/rpz")


def ensure_directories():
    """
    Ensure runtime directories exist.
    """

    for directory in (DOWNLOAD_DIR, RPZ_DIR):
        directory.mkdir(parents=True, exist_ok=True)


# -----------------------------
# RPZ generation
# -----------------------------


def write_rpz(blocklist, domains):

    rpz_path = RPZ_DIR / f"{blocklist.id}.rpz"

    logger.log(f"Generating RPZ for {blocklist.name} ({len(domains)} domains)")

    with open(rpz_path, "w", encoding="utf-8") as f:
        f.write("$TTL 2h\n")
        f.write("@ IN SOA localhost. root.localhost. 1 1h 15m 30d 2h\n")
        f.write("  IN NS localhost.\n\n")

        for domain in sorted(domains):
            f.write(f"{domain} CNAME .\n")

    return rpz_path


# -----------------------------
# Unbound config generation
# -----------------------------


def write_unbound_config(blocklist, rpz_path):

    conf_path = pathlib.Path(f"/etc/unbound/unbound.conf.d/janr-{blocklist.id}.conf")

    content = f'rpz:\n  name: "{blocklist.id}"\n  zonefile: "{rpz_path}"\n'

    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(content)

    return conf_path


# -----------------------------
# deployment
# -----------------------------


def deploy_blocklist(blocklist):

    all_domains = set()

    for asset_cfg in getattr(blocklist, "assets", []):
        logger.log(f"asset_cfg: {asset_cfg}")
        asset = Asset(asset_cfg)
        logger.log(f"Processing asset {asset.id} ({asset.config.feed})")

        try:
            domains = asset.run()
            all_domains.update(domains)

        except Exception as e:
            logger.log(f"Asset failed {asset.id}: {e}", logger.ERROR)
            continue

    rpz_path = write_rpz(blocklist, all_domains)
    write_unbound_config(blocklist, rpz_path)


# -----------------------------
# unbound reload
# -----------------------------


def restart_unbound():

    logger.log("Restarting unbound")

    subprocess.run(
        ["systemctl", "restart", "janr-unbound"],
        check=True,
    )


# -----------------------------
# main
# -----------------------------


def main():

    ensure_directories()

    # bootstrap plugins (feeds, datasets, parsers)
    PluginManager.discover("plugins.feeds")
    PluginManager.discover("plugins.datasets")
    PluginManager.discover("plugins.parsers")

    enabled = [b for b in BLOCKLISTS if b.enabled]

    if not enabled:
        logger.log("No enabled blocklists found", logger.WARNING)
        return

    for blocklist in enabled:
        try:
            logger.log(f"Deploying blocklist: {blocklist.name}")
            deploy_blocklist(blocklist)

        except Exception as e:
            logger.log(f"Failed blocklist {blocklist.name}: {e}", logger.ERROR)
            continue

    restart_unbound()

    logger.log("Blocklist deployment complete")


if __name__ == "__main__":
    main()
