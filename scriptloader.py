import imp

import nose.loader
import nose.plugins

class ScriptLoader(nose.plugins.Plugin):
    """Load tests from scripts that may not have a .py extension."""

    def options(self, parser, env):
        return nose.plugins.Plugin.options(self, parser, env)

    def configure(self, options, conf):
        return nose.plugins.Plugin.configure(self, options, conf)

    def prepareTestLoader(self, loader):
        """Save the *loader*.

        This instance will be used later by :meth:`loadTestsFromFile` if
        necessary.
        """
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
        except SyntaxError:
            return None

        return self.loader.loadTestsFromModule(module)
