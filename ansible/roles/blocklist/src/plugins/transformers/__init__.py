from .base import Transformer

__all__ = ["Transformer"]

# from plugins.plugin_manager import PluginManager
# from .base import Transformer

# class TransformerPluginManager(PluginManager):

#     plugin_base_class = Transformer

# manager = TransformerPluginManager(
#     package_name=__name__,
#     package_path=__path__,
# )

# manager.discover()

# TRANSFORMER_REGISTRY = manager.registry