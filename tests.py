import os
import unittest

TESTDATA = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "testdata")

class FakeLoader(object):

    def loadTestsFromModule(self, module):
        return module

class TestScriptLoader(unittest.TestCase):

    def setUp(self):
        import os

        from scriptloader import ScriptLoader

        self.plugin = ScriptLoader()
        self.plugin.loader = FakeLoader()

        self._data = []

    def tearDown(self):
        for fname in self._data:
            cfile = fname + 'c'
            if os.path.exists(cfile):
                os.remove(cfile)

    def data(self, name):
        path = os.path.join(TESTDATA, name)
        self._data.append(path)

        return path

    def test_instance(self):
        """Test plugin instantiation."""
        from scriptloader import ScriptLoader

        scriptloader = ScriptLoader()

        self.assertEqual(scriptloader.name, "scriptloader")

    def test_prepareTestLoader(self):
        """Make sure we get a loader instance."""
        self.plugin.loader = None
        loader = FakeLoader()

        self.plugin.prepareTestLoader(loader)

        self.assertEqual(loader, self.plugin.loader)

    def test_loadTestsFromFile(self):
        """Test loading from a valid script."""
        testfile = self.data("script")

        result = self.plugin.loadTestsFromFile(testfile)

        spam = getattr(result, "spam", None)
        self.assertTrue(hasattr(result, "TestFoo"))
        self.assertEqual(spam, None)

    def test_loadTestsFromFile_notascript(self):
        """Test loading from a file that's not a valid script."""
        testfile = self.data("notascript")

        result = self.plugin.loadTestsFromFile(testfile)

        self.assertEqual(result, False)
