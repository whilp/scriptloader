import imp

import nose.loader
import nose.plugins

class ScriptLoader(nose.plugins.Plugin):

    def options(self, parser, env):
        return nose.plugins.Plugin.options(self, parser, env)

    def configure(self, options, conf):
        return nose.plugins.Plugin.configure(self, options, conf)

    def prepareTestLoader(self, loader):
        self.loader = loader

    def loadTestsFromFile(self, filename):
        try:
            module = imp.load_source("module", filename)
        except SyntaxError:
            return False

        return self.loader.loadTestsFromModule(module)
