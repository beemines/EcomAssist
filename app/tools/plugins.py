"""Only administrator-owned local configuration may nominate import entries."""
from importlib import import_module

from app.tools.catalog import ToolCatalog


class PluginLoader:
    def __init__(self):
        self._loaded = set()

    def load(self, catalog: ToolCatalog, entries: tuple[str, ...]) -> None:
        for entry in entries:
            if entry in self._loaded:
                continue
            # Register on an unpublished staging catalog: a failed plugin is atomic.
            staging = ToolCatalog()
            staging._registrations = dict(catalog._registrations)
            import_module(entry).register(staging)
            catalog._registrations = staging._registrations
            self._loaded.add(entry)
