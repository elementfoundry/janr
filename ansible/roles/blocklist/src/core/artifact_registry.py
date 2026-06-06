#!/usr/bin/env python3

from collections import defaultdict


class ArtifactRegistry:
    def __init__(self):
        # blocklist_id -> bool
        self._preserve = {}

        # blocklist_id -> set(download paths)
        self._downloads = defaultdict(set)

    # -----------------------------
    # registration
    # -----------------------------

    def register(self, blocklist_id: str, preserve_artifacts: bool):
        self._preserve[blocklist_id] = preserve_artifacts

    def should_preserve(self, blocklist_id: str) -> bool:
        return self._preserve.get(blocklist_id, False)

    # -----------------------------
    # downloads
    # -----------------------------

    def add_download(self, blocklist_id: str, path: str):
        self._downloads[blocklist_id].add(path)

    def download_artifacts(self, blocklist_id: str):
        return self._downloads.get(blocklist_id, set())

    def registered_assets(self):
        return self._preserve.keys()


artifact_registry = ArtifactRegistry()

# # core/artifact_registry.py

# from collections import defaultdict
# from pathlib import Path


# class ArtifactRegistry:
#     """
#     Central registry for artifact lifecycle decisions.

#     Tracks:
#     - asset-level preservation policy
#     - rpz artifacts
#     - download artifacts
#     """

#     def __init__(self):
#         # asset_id -> preserve flag
#         self._assets = {}

#         # asset_id -> set(Path)
#         self._rpz_artifacts = defaultdict(set)

#         # asset_id -> set(Path)
#         self._download_artifacts = defaultdict(set)

#     # -----------------------------
#     # asset policy
#     # -----------------------------

#     def register(self, asset_id: str, preserve_artifacts: bool):
#         """
#         Register asset-level preservation policy.
#         """
#         self._assets[asset_id] = preserve_artifacts

#     def preserve(self, asset_id: str) -> bool:
#         """
#         True if ALL artifacts for this asset should be preserved.
#         """
#         return self._assets.get(asset_id, False)

#     def registered_assets(self):
#         return self._assets.keys()

#     # -----------------------------
#     # artifact tracking
#     # -----------------------------

#     def register_rpz(self, asset_id: str, path: Path):
#         """
#         Track an RPZ artifact created by an asset.
#         """
#         self._rpz_artifacts[asset_id].add(Path(path))

#     def register_download(self, asset_id: str, path: Path):
#         """
#         Track a download artifact created by an asset.
#         """
#         self._download_artifacts[asset_id].add(Path(path))

#     # -----------------------------
#     # artifact access
#     # -----------------------------

#     def rpz_artifacts(self, asset_id: str):
#         return self._rpz_artifacts.get(asset_id, set())

#     def download_artifacts(self, asset_id: str):
#         return self._download_artifacts.get(asset_id, set())

#     def all_rpz_artifacts(self):
#         for paths in self._rpz_artifacts.values():
#             yield from paths

#     def all_download_artifacts(self):
#         for paths in self._download_artifacts.values():
#             yield from paths

#     # -----------------------------
#     # cleanup decision helpers
#     # -----------------------------

#     def should_preserve(self, asset_id: str) -> bool:
#         """
#         Central decision point:
#         if asset is marked as preserved,
#         all artifacts are preserved.
#         """
#         return self.preserve(asset_id)


# artifact_registry = ArtifactRegistry()
