import imp

import nose.loader
import nose.plugins

class NoseScript(nose.plugins.Plugin):

    def loadTestsFromFile(self, filename):
        try:
            module = imp.load_source("module", filename)
        except SyntaxError:
            return False

        return self.loadTestsFromModule(module)
