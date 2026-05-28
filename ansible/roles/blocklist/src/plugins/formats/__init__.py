from .base import Format
# from .plaintext_format_plugin import PlaintextFormatPlugin

__all__ = ["Format"]

# from plugins.plugin_manager import PluginManager
# from .base import Format

# class FormatPluginManager(PluginManager):

#     plugin_base_class = Format

# manager = FormatPluginManager(
#     package_name=__name__,
#     package_path=__path__,
# )

# manager.discover()

# FORMAT_REGISTRY = manager.registry