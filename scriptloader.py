import imp

import nose.failure
import nose.loader
import nose.plugins
import nose.selector
import nose.suite
import nose.util

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
    
    def loadTestsFromName(self, name, module=None, discovered=False):
        """Load tests from the entity with the given *name*.

        If *name* is a filename, attempt to load it using
        :func:`imp.load_source`. If that succeeds, search for a matching name in
        the loaded module.
        """
        addr = nose.selector.TestAddress(name, workingDir=self.loader.workingDir)
        path = addr.filename
        if not path:
            return self.loader.loadTestsFromName(name, module=module, discovered=discovered)

        module = getpackage(path)
        if module is None:
            try:
                module = imp.load_source("module", path)
            except SyntaxError:
                return

        suite = self.loader.suiteClass
        if addr.call:
            name = addr.call
        parent, obj = self.loader.resolve(name, module)
        if (nose.util.isclass(parent)
                and getattr(parent, '__module__', None) != module.__name__):
            parent = nose.util.transplant_class(parent, module.__name__)
            obj = getattr(parent, obj.__name__)
        if isinstance(obj, nose.failure.Failure):
            return suite([obj])
        else:
            return suite(nose.suite.ContextList([self.loader.makeTest(obj, parent)],
                context=parent))
