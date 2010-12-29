import inspect
import os
import shutil
import tempfile
import unittest

TESTDATA = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "testdata")

def fake_load_source(name, path):
    return name

class FakeModule(object):
    pass

class FakeLoader(object):

    def loadTestsFromModule(self, module):
        return module

    def loadTestsFromName(self, name, module=None, discovered=False):
        return name

class FakeAddress(object):
    pass

class TestScriptLoader(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        from scriptloader import ScriptLoader

        self.plugin = ScriptLoader()
        self.plugin.loadedTestsFromName = False
        self.plugin.loader = FakeLoader()
        self.addr = FakeAddress()

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
        result = self.plugin.loadTestsFromFile("fake file", loader=fake_load_source)

        self.assertEqual(result, "module")

    def test_loadTestsFromFile(self):
        """Test loading from a script that raises SyntaxError."""
        def fake_load_bad_source(name, path):
            raise SyntaxError()
        result = self.plugin.loadTestsFromFile("fake file", loader=fake_load_bad_source)

        self.assertEqual(result, None)

    def test_loadTestsFromName(self):
        self.addr.filename = "a path"
        self.addr.call = "call"

        result = self.plugin.loadTestsFromName("foo", addr=self.addr,
                loader=fake_load_source)

        self.assertEqual(self.plugin.loadedTestsFromName, True)
        self.assertEqual(result, "call")

    def test_loadTestsFromName_badsyntax(self):
        self.addr.filename = "a path"
        self.addr.call = "call"

        def fake_load_bad_source(name, path):
            raise SyntaxError()

        result = self.plugin.loadTestsFromName("foo", addr=self.addr,
                loader=fake_load_bad_source)

        self.assertEqual(self.plugin.loadedTestsFromName, False)
        self.assertEqual(result, None)

    def test_loadTestsFromName_nofilename(self):
        self.addr.filename = ""

        result = self.plugin.loadTestsFromName("foo", addr=self.addr)

        self.assertEqual(result, None)

    def test_loadTestsFromName_secondtime(self):
        self.plugin.loadedTestsFromName = True
        result = self.plugin.loadTestsFromName("foo")

        self.assertEqual(result, None)

    def test_loadTestsFromName_module(self):
        result = self.plugin.loadTestsFromName("foo", module="a module")

        self.assertEqual(result, None)

class TestLoadSource(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        from scriptloader import load_source

        self.load_source = load_source
        self.tmpdir = tempfile.mkdtemp(prefix="scriptloader-test-")
        self.oldcwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir)
        os.chdir(self.oldcwd)

    def data(self, name):
        src = os.path.join(TESTDATA, name)
        dst = os.path.join(self.tmpdir, name)
        shutil.copy(src, dst)

        return dst
    
    def test_load_source(self):
        src = self.data("script")
        
        result = self.load_source("script", src)

        self.assertEqual(result.__name__, "script")
        self.assertEqual(result.__file__, src)
        self.assertEqual(inspect.getfile(result.test_bar), src)
        self.assertEqual(os.listdir(self.tmpdir), [os.path.basename(src)])
