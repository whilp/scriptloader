import imp
import logging
import sys

import nose.failure
import nose.loader
import nose.plugins
import nose.selector
import nose.suite
import nose.util

try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record): pass

log = logging.getLogger("nose.plugins.%s" % __name__)
log.addHandler(NullHandler())

def load_source(name, path, bytecode=False):
    """Load a module from *path*.

    :param bytecode: if False, :data:`sys.dont_write_bytecode` will be set to
        True (if present). :data:`sys.dont_write_bytecode` is only available in
        Python >= 2.6.

    .. versionadded:: 0.2.0
    """
    dont_write_bytecode = getattr(sys, "dont_write_bytecode", None)
    if dont_write_bytecode is not None and bytecode is False:
        sys.dont_write_bytecode = True

    try:
        module = imp.load_source(name, path)
    finally:
        if dont_write_bytecode is not None and bytecode is False:
            sys.dont_write_bytecode = False

    return module

class ScriptLoader(nose.plugins.Plugin):
    """Load tests from scripts that may not have a .py extension."""

    def options(self, parser, env):
        return nose.plugins.Plugin.options(self, parser, env)

    def configure(self, options, conf):
        self.loadedTestsFromName = False
        return nose.plugins.Plugin.configure(self, options, conf)

    def prepareTestLoader(self, loader):
        """Save the *loader*.

        This instance will be used later by :meth:`loadTestsFromFile` if
        necessary.
        """
        log.debug("saving loader instance")
        self.loader = loader

    def loadTestsFromFile(self, filename, loader=load_source):
        """Load tests from *filename*.

        Attempt to load the file using :func:`imp.load_source`. If that
        succeeds, pass the loaded module to the :attr:`loader`
        :meth:`loadTestsFromModule`. If the file can't be loaded, return None
        so other plugins can try loading it.
        """
        try:
            module = loader("module", filename)
            log.debug("loaded module from file %r", filename)
        except SyntaxError:
            return None

        return self.loader.loadTestsFromModule(module)
    
    def loadTestsFromName(self, name, module=None, discovered=False,
            addr=None, loader=load_source):
        """Load tests from the entity with the given *name*.

        If *name* is a filename, attempt to load it using
        :func:`imp.load_source`. If that succeeds, search for a matching name in
        the loaded module.
        """
        if module or self.loadedTestsFromName or ":" not in name:
            return None

        if addr is None: # pragma: nocover
            addr = nose.selector.TestAddress(name, workingDir=self.loader.workingDir)
        path = addr.filename
        if not path:
            return None

        try:
            module = loader("module", path)
        except SyntaxError:
            return None

        name = addr.call
        log.debug("loaded tests from name %s at file %r", name, path)
        self.loadedTestsFromName = True
        return self.loader.loadTestsFromName(name, module=module,
            discovered=discovered)
