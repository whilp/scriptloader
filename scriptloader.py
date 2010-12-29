import imp
import logging

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

    def loadTestsFromFile(self, filename):
        """Load tests from *filename*.

        Attempt to load the file using :func:`imp.load_source`. If that
        succeeds, pass the loaded module to the :attr:`loader`
        :meth:`loadTestsFromModule`. If the file can't be loaded, return None
        so other plugins can try loading it.
        """
        try:
            module = imp.load_source("module", filename)
            log.debug("loaded module from file %r", filename)
        except SyntaxError:
            return None

        return self.loader.loadTestsFromModule(module)
    
    def loadTestsFromName(self, name, module=None, discovered=False):
        """Load tests from the entity with the given *name*.

        If *name* is a filename, attempt to load it using
        :func:`imp.load_source`. If that succeeds, search for a matching name in
        the loaded module.
        """
        if module or self.loadedTestsFromName:
            return None

        addr = nose.selector.TestAddress(name, workingDir=self.loader.workingDir)
        path = addr.filename
        if path:
            try:
                module = imp.load_source("module", path)
            except SyntaxError:
                return None

        name = addr.call
        log.debug("loaded tests from name %s at file %r", name, path)
        self.loadedTestsFromName = True
        return self.loader.loadTestsFromName(name, module=module,
            discovered=discovered)
