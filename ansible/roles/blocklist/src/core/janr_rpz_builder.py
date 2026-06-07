#!/usr/bin/env python3

from collections import defaultdict
from pathlib import Path

from core.artifact_registry import artifact_registry
from core.logger import logger


class JANRRPZBuilder:
    def __init__(self):

        # domain -> set of source files
        self.domain_index = defaultdict(set)

        # blocklist_id -> rpz artifact path
        self.source_files = {}

        # collapse policy
        self.collapse_roots = self._load_collapse_policy()

    # -----------------------------
    # collapse policy
    # -----------------------------

    def _load_collapse_policy(self):

        policy_file = Path("/opt/janr/blocklist/policies/collapse.txt")

        domains = set()

        if not policy_file.exists():
            logger.log(
                f"Collapse policy not found: {policy_file}",
                logger.WARNING,
            )
            return domains

        try:
            with policy_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().lower()

                    if not line:
                        continue

                    if line.startswith("#"):
                        continue

                    domains.add(line)

            logger.log(f"Loaded {len(domains)} collapse domains")

        except Exception as e:
            logger.log(
                f"Failed loading collapse policy: {e}",
                logger.ERROR,
            )

        return domains

    def _collapse_domain(self, domain: str) -> str:
        """
        Collapse domains listed in collapse.txt.

        Example:

            ads.doubleclick.net
            pubads.g.doubleclick.net

        become:

            doubleclick.net
        """

        for root in self.collapse_roots:
            if domain == root:
                return root

            if domain.endswith("." + root):
                return root

        return domain

    # -----------------------------
    # normalization
    # -----------------------------

    def normalize_domain(self, domain: str) -> str:
        return domain.strip().lower().rstrip(".")

    # -----------------------------
    # ingestion
    # -----------------------------

    def ingest_rpz_file(self, blocklist_id: str, file_path: Path):
        """
        Ingest RPZ artifact tied to blocklist_id.
        """

        logger.log(f"Ingesting RPZ artifact: {file_path.name}")

        self.source_files[blocklist_id] = file_path

        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("$") or line.startswith(";"):
                        continue

                    if "SOA" in line or "NS" in line:
                        continue

                    parts = line.split()

                    if not parts:
                        continue

                    domain = self.normalize_domain(parts[0])

                    if not domain:
                        continue

                    if domain.startswith("@"):
                        continue

                    collapsed = self._collapse_domain(domain)

                    if collapsed != domain:
                        logger.log(f"Collapsed {domain} -> {collapsed}")

                    self.domain_index[collapsed].add(file_path)

        except Exception as e:
            logger.log(
                f"Failed parsing RPZ artifact {file_path.name}: {e}",
                logger.ERROR,
            )

    # -----------------------------
    # finalize
    # -----------------------------

    def finalize(
        self,
        output_dir: Path,
        output_name: str = "janr-unified.rpz",
    ):

        output_path = Path(output_dir) / output_name

        logger.log(f"Writing unified RPZ -> {output_path}")

        try:
            with output_path.open("w", encoding="utf-8") as f:
                f.write("$TTL 2h\n")
                f.write("@ IN SOA localhost. root.localhost. 1 1h 15m 30d 2h\n")
                f.write("  IN NS localhost.\n\n")

                for domain in sorted(self.domain_index.keys()):
                    f.write(f"{domain} CNAME .\n")

            logger.log(
                f"Unified RPZ written successfully "
                f"({len(self.domain_index)} unique domains)"
            )

            self._cleanup_artifacts()

        except Exception as e:
            logger.log(
                f"Failed writing unified RPZ: {e}",
                logger.ERROR,
            )
            raise

    # -----------------------------
    # cleanup
    # -----------------------------

    def _cleanup_artifacts(self):

        logger.log("Starting artifact cleanup")

        # -------------------------
        # RPZ artifact cleanup
        # -------------------------

        for blocklist_id, file_path in self.source_files.items():
            if artifact_registry.should_preserve(blocklist_id):
                logger.log(f"Preserving RPZ artifact: {file_path.name}")
                continue

            try:
                file_path.unlink(missing_ok=True)

                logger.log(f"Deleted RPZ artifact: {file_path.name}")

            except Exception as e:
                logger.log(
                    f"Failed deleting RPZ artifact {file_path.name}: {e}",
                    logger.ERROR,
                )

        # -------------------------
        # Download artifact cleanup
        # -------------------------

        for blocklist_id in artifact_registry.registered_assets():
            if artifact_registry.should_preserve(blocklist_id):
                logger.log(f"Preserving downloads for {blocklist_id}")
                continue

            for path in artifact_registry.download_artifacts(blocklist_id):
                try:
                    Path(path).unlink(missing_ok=True)

                    logger.log(f"Deleted download artifact: {path}")

                except Exception as e:
                    logger.log(
                        f"Failed deleting download {path}: {e}",
                        logger.ERROR,
                    )


janr_rpz_builder = JANRRPZBuilder()

# #!/usr/bin/env python3

# from collections import defaultdict
# from pathlib import Path

# from core.artifact_registry import artifact_registry
# from core.janr_logger import logger

# # -----------------------------
# # collapse policy loader
# # -----------------------------


# def load_collapse_policy(path: Path) -> set[str]:
#     """
#     Load explicit collapse targets from collapse.txt.

#     This is deterministic and the ONLY source of collapsing behavior.
#     """

#     domains = set()

#     try:
#         with path.open("r", encoding="utf-8") as f:
#             for line in f:
#                 line = line.strip()

#                 if not line or line.startswith("#"):
#                     continue

#                 domains.add(line.lower().rstrip("."))

#     except FileNotFoundError:
#         logger.log(
#             f"Collapse policy missing: {path} (no collapsing applied)",
#             logger.WARNING,
#         )

#     return domains


# # -----------------------------
# # builder
# # -----------------------------


# class JANRRPZBuilder:
#     def __init__(self):

#         # domain -> set of source RPZ files
#         self.domain_index = defaultdict(set)

#         # RPZ artifacts explicitly ingested
#         self.source_files = set()

#         # -----------------------------
#         # COLLAPSE POLICY (SOURCE OF TRUTH)
#         # -----------------------------
#         self.collapse_policy = load_collapse_policy(
#             Path("/opt/janr/blocklist/policies/collapse.txt")
#         )

#     # -----------------------------
#     # normalization
#     # -----------------------------

#     def normalize_domain(self, domain: str) -> str:
#         return domain.strip().lower().rstrip(".")

#     # -----------------------------
#     # collapsing (STRICT + DETERMINISTIC)
#     # -----------------------------

#     def _collapse_domain(self, domain: str) -> str:
#         """
#         Collapse only if explicitly listed in collapse.txt.

#         No heuristics. No inference. No guessing.
#         """

#         parts = domain.split(".")

#         if len(parts) < 2:
#             return domain

#         root = ".".join(parts[-2:])

#         if root in self.collapse_policy:
#             logger.log(f"COLLAPSING {domain} → {root}")
#             return root

#         return domain

#     # -----------------------------
#     # ingestion
#     # -----------------------------

#     def ingest_rpz_file(self, file_path: Path):
#         """
#         Ingest a single RPZ artifact file produced by a blocklist.
#         Applies deterministic collapse policy during ingestion.
#         """

#         logger.log(f"Ingesting RPZ artifact: {file_path.name}")

#         self.source_files.add(file_path)

#         try:
#             with file_path.open("r", encoding="utf-8") as f:
#                 for line in f:
#                     line = line.strip()

#                     if not line:
#                         continue

#                     if line.startswith("$") or line.startswith(";"):
#                         continue

#                     if "SOA" in line or "NS" in line:
#                         continue

#                     parts = line.split()

#                     if not parts:
#                         continue

#                     domain = self.normalize_domain(parts[0])

#                     if not domain:
#                         continue

#                     if domain.startswith("@"):
#                         continue

#                     # -----------------------------
#                     # APPLY COLLAPSE POLICY HERE
#                     # -----------------------------
#                     domain = self._collapse_domain(domain)

#                     self.domain_index[domain].add(file_path)

#         except Exception as e:
#             logger.log(
#                 f"Failed parsing RPZ artifact {file_path.name}: {e}",
#                 logger.ERROR,
#             )

#     # -----------------------------
#     # finalize (build unified RPZ)
#     # -----------------------------

#     def finalize(
#         self,
#         output_dir: Path,
#         output_name: str = "janr-unified.rpz",
#     ):
#         """
#         Write final unified RPZ and trigger artifact cleanup.
#         """

#         output_path = Path(output_dir) / output_name

#         logger.log(f"Writing unified RPZ -> {output_path}")

#         try:
#             with output_path.open("w", encoding="utf-8") as f:
#                 f.write("$TTL 2h\n")
#                 f.write("@ IN SOA localhost. root.localhost. 1 1h 15m 30d 2h\n")
#                 f.write("  IN NS localhost.\n\n")

#                 for domain in sorted(self.domain_index.keys()):
#                     f.write(f"{domain} CNAME .\n")

#             logger.log("Unified RPZ written successfully")

#             self._cleanup_artifacts()

#         except Exception as e:
#             logger.log(
#                 f"Failed writing unified RPZ: {e}",
#                 logger.ERROR,
#             )
#             raise

#     # -----------------------------
#     # cleanup (UNCHANGED LOGIC)
#     # -----------------------------

#     def _cleanup_artifacts(self):
#         """
#         Clean up ALL artifacts:
#         - RPZ artifacts (ingested files)
#         - download artifacts (registry-tracked)
#         """

#         logger.log("Starting artifact cleanup")

#         # -------------------------
#         # 1. CLEAN RPZ ARTIFACTS
#         # -------------------------
#         for file_path in sorted(self.source_files):
#             asset_id = file_path.stem

#             if artifact_registry.should_preserve(asset_id):
#                 logger.log(f"Preserving RPZ artifact: {file_path.name}")
#                 continue

#             try:
#                 file_path.unlink()
#                 logger.log(f"Deleted RPZ artifact: {file_path.name}")

#             except Exception as e:
#                 logger.log(
#                     f"Failed to delete RPZ artifact {file_path.name}: {e}",
#                     logger.ERROR,
#                 )

#         # -------------------------
#         # 2. CLEAN DOWNLOAD ARTIFACTS (UNCHANGED)
#         # -------------------------
#         for asset_id in artifact_registry.registered_assets():
#             downloads = artifact_registry.download_artifacts(asset_id)

#             if not downloads:
#                 continue

#             if artifact_registry.should_preserve(asset_id):
#                 logger.log(f"Preserving download artifacts for asset {asset_id}")
#                 continue

#             for path in downloads:
#                 try:
#                     Path(path).unlink(missing_ok=True)

#                     logger.log(f"Deleted download artifact: {path}")

#                 except Exception as e:
#                     logger.log(
#                         f"Failed to delete download {path}: {e}",
#                         logger.ERROR,
#                     )


# # global singleton instance
# janr_rpz_builder = JANRRPZBuilder()
