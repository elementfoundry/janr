#!/usr/bin/env python3

import subprocess
import traceback
from pathlib import Path

from core.asset import Asset
from core.janr_logger import logger
from core.janr_rpz_builder import janr_rpz_builder
from janr_blocklists import BLOCKLISTS
from plugins.plugin_manager import PluginManager

# -----------------------------
# paths
# -----------------------------

ARTIFACT_RPZ_DIR = Path("/run/janr/blocklist/artifacts/rpz")
FINAL_RPZ_DIR = Path("/run/janr/blocklist/rpz")

UNBOUND_CONF = Path("/etc/unbound/unbound.conf.d/janr-unified.conf")
FINAL_RPZ = FINAL_RPZ_DIR / "janr-unified.rpz"


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
# boot repair
# -----------------------------


def repair_unbound_rpz_state():

    if FINAL_RPZ.exists():
        return

    if not UNBOUND_CONF.exists():
        return

    logger.log(f"RPZ missing but unbound include exists; removing {UNBOUND_CONF}")

    UNBOUND_CONF.unlink()

    logger.log("Restarting unbound to clear stale RPZ configuration")

    subprocess.run(
        ["systemctl", "restart", "janr-unbound"],
        check=True,
    )


# -----------------------------
# unbound include
# -----------------------------


def ensure_unbound_include():

    if UNBOUND_CONF.exists():
        return

    logger.log(f"Creating {UNBOUND_CONF}")

    UNBOUND_CONF.write_text(
        f"""rpz:
  name: "janr-unified"
  zonefile: "{FINAL_RPZ}"
""",
        encoding="utf-8",
    )


# -----------------------------
# main pipeline
# -----------------------------


def main():

    # -------------------------
    # boot repair
    # -------------------------
    repair_unbound_rpz_state()

    # -------------------------
    # bootstrap plugins
    # -------------------------

    PluginManager.discover("plugins.feeds")
    PluginManager.discover("plugins.datasets")
    PluginManager.discover("plugins.parsers")

    enabled = [b for b in BLOCKLISTS if b.enabled]

    if not enabled:
        logger.log("No enabled blocklists found", logger.WARNING)
        return

    # -------------------------
    # ingestion stage
    # -------------------------

    for blocklist in enabled:
        try:
            logger.log(f"Deploying blocklist: {blocklist.name}")

            all_domains = set()

            # ---------------------
            # asset execution stage
            # ---------------------

            for asset_cfg in getattr(blocklist, "assets", []):
                asset = Asset(asset_cfg, blocklist.id)

                logger.log(f"Processing asset {asset.id} ({asset.feed_name})")

                domains = asset.run()

                if domains:
                    all_domains.update(domains)

            # ---------------------
            # write RPZ artifact (blocklist-owned)
            # ---------------------

            rpz_path = ARTIFACT_RPZ_DIR / f"{blocklist.id}.rpz"

            logger.log(
                f"Writing RPZ artifact for {blocklist.name} "
                f"({len(all_domains)} domains)"
            )

            with rpz_path.open("w", encoding="utf-8") as f:
                f.write("$TTL 2h\n")
                f.write("@ IN SOA localhost. root.localhost. 1 1h 15m 30d 2h\n")
                f.write("  IN NS localhost.\n\n")

                for domain in sorted(all_domains):
                    f.write(f"{domain} CNAME .\n")

            # ---------------------
            # ingest into builder (blocklist-aware)
            # ---------------------

            janr_rpz_builder.ingest_rpz_file(blocklist.id, rpz_path)

        except Exception as e:
            logger.log(
                f"Failed blocklist {blocklist.name}: {e}",
                logger.ERROR,
            )
            logger.log(traceback.format_exc())
            continue

    # -------------------------
    # build stage
    # -------------------------

    logger.log(f"Indexed {len(janr_rpz_builder.domain_index)} unique domains")

    janr_rpz_builder.finalize(
        output_dir=FINAL_RPZ_DIR,
        output_name="janr-unified.rpz",
    )

    # -------------------------
    # unbound include
    # -------------------------

    ensure_unbound_include()

    # -------------------------
    # reload stage
    # -------------------------

    restart_unbound()

    logger.log("Blocklist deployment complete")


if __name__ == "__main__":
    main()
