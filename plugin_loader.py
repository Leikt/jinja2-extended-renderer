from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from types import ModuleType
from typing import Optional, Callable, Type

import jinja2
import jinja2.ext


def _import_module(logger: logging.Logger, path: str) -> Optional[ModuleType]:
    """Dynamically load the module."""
    try:
        return importlib.import_module(path)
    except ModuleNotFoundError as ex:
        logger.critical(ex.msg)
    return None


class PluginManager:
    """Manage the plugins."""

    def __init__(self, logger: logging.Logger, j2_env: jinja2.Environment):
        self._logger = logger
        self._j2_env = j2_env
        self._loaders = {
            J2Filter: self._load_jinja2_filter,
            J2Global: self._load_jinja2_global,
            J2Extension: self._load_jinja2_extension
        }

    def load_plugin(self, plugin_path: str):
        """Load the given plugin into the manager."""
        self._logger.debug(f'Loading plugin: {plugin_path}...')
        module = _import_module(self._logger, plugin_path)
        if module is None:
            return
        self._logger.debug(f'Module loaded: {plugin_path}')

        if not hasattr(module, 'load_plugin'):
            self._logger.critical(f'{plugin_path} does not have the required "load_plugin" method')
            return

        loader = getattr(module, 'load_plugin')
        components = loader(self._j2_env)

        if len(components) == 0:
            self._logger.warning(f'{plugin_path} is empty. It will be ignored')
            return
        self._logger.debug(f'{len(components)} components found in {plugin_path}')

        for i, component in enumerate(components, start=1):
            self._logger.debug(f'Loading component...{i:>5}/{len(components)}')
            self._load_component(component)

        self._logger.debug(f'Plugin {plugin_path} loaded')

    def _load_component(self, component):
        """Load a specific component into the manager."""
        loader = self._loaders.get(type(component))
        if loader is None:
            self._logger.warning(f'Invalid plugin component type: {type(component)}. Component ignored')
            return
        loader(component)  # type: ignore

    def _load_jinja2_filter(self, component: J2Filter):
        """Load the filter into the jinja2 environment."""
        function = component.function
        name = component.name
        if name in self._j2_env.filters:
            self._logger.warning(f'There already is a jinja2 filter named "{name}" the older one will be erased.')
        self._j2_env.filters[name] = function

    def _load_jinja2_global(self, component: J2Global):
        """Load the global method into the jinja2 environment."""
        function = component.function
        name = component.name
        if name in self._j2_env.globals:
            self._logger.warning(f'There already is a jinja2 global named "{name}" the older one will be erased.')
        self._j2_env.globals[name] = function

    def _load_jinja2_extension(self, component: J2Extension):
        """Load the extension into the jinja2 environment."""
        extension = component.extension
        self._j2_env.add_extension(extension)


@dataclass
class J2Filter:
    function: Callable
    name: str


@dataclass
class J2Global:
    function: Callable
    name: str


@dataclass
class J2Extension:
    extension: Type[jinja2.ext.Extension]
