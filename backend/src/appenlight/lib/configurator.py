import inspect
import logging

from pyramid.config import Configurator

log = logging.getLogger(__name__)


class InspectProxy(object):
    """
    Proxy to the `inspect` module that allows us to use the pyramid include
    mechanism for cythonized modules without source file.
    """

    def _get_cyfunction_func_code(self, cyfunction):
        """
        Unpack the `func_code` attribute of a cython function.
        """
        if inspect.ismethod(cyfunction):
            cyfunction = cyfunction.im_func
        return getattr(cyfunction, "func_code")

    def getmodule(self, *args, **kwds):
        """
        Simple proxy to `inspect.getmodule`.
        """
        return inspect.getmodule(*args, **kwds)

    def getsourcefile(self, obj):
        """
        Proxy to `inspect.getsourcefile` or `inspect.getfile` depending on if
        it's called to look up the source file that contains the magic pyramid
        `includeme` callable.

        For cythonized modules the source file may be deleted. Therefore we
        return the result of `inspect.getfile` instead. In the case of the
        `configurator.include` method this is OK, because the result is passed
        to `os.path.dirname` which strips the file name. So it doesn't matter
        if we return the path to the source file or another file in the same
        directory.
        """
        # Check if it's called to look up the source file that contains the
        # magic pyramid `includeme` callable.
        if getattr(obj, "__name__") == "includeme":
            try:
                return inspect.getfile(obj)
            except TypeError as e:
                # Cython functions are not recognized as functions by the
                # inspect module. We have to unpack the func_code attribute
                # ourself.
                if "cyfunction" in e.message:
                    obj = self._get_cyfunction_func_code(obj)
                    return inspect.getfile(obj)
                raise
        else:
            return inspect.getsourcefile(obj)


class CythonCompatConfigurator(Configurator):
    """
    Customized configurator to replace the inspect class attribute with
    a custom one that is cython compatible.
    """

    inspect = InspectProxy()


def register_appenlight_plugin(config, plugin_name, plugin_config):
    def register():
        log.warning("Registering plugin: {}".format(plugin_name))
        if plugin_name not in config.registry.appenlight_plugins:
            config.registry.appenlight_plugins[plugin_name] = {
                "javascript": None,
                "static": None,
                "css": None,
                "celery_tasks": None,
                "celery_beats": None,
                "fulltext_indexer": None,
                "sqlalchemy_migrations": None,
                "default_values_setter": None,
                "header_html": None,
                "resource_types": [],
                "url_gen": None,
            }
        config.registry.appenlight_plugins[plugin_name].update(plugin_config)
        # inform AE what kind of resource types we have available
        # so we can avoid failing when a plugin is removed but data
        # is still present in the db
        if plugin_config.get("resource_types"):
            config.registry.resource_types.extend(plugin_config["resource_types"])

    config.action("appenlight_plugin={}".format(plugin_name), register)
