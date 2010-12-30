import inspect
import logging
import os
import shutil
import subprocess
import tempfile
import unittest

TESTDATA = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "testdata")

try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record): pass

log = logging.getLogger("scriptloader.tests")
log.addHandler(NullHandler())

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

        self.assertEqual(result, "fake file")

    def test_loadTestsFromFile_badsyntax(self):
        """Test loading from a script that raises SyntaxError."""
        def fake_load_bad_source(name, path):
            raise SyntaxError()
        result = self.plugin.loadTestsFromFile("fake file", loader=fake_load_bad_source)

        self.assertEqual(result, None)

    def test_loadTestsFromName(self):
        """Test loading by name."""
        self.addr.filename = "a path"
        self.addr.call = "call"

        result = self.plugin.loadTestsFromName("foo:bar", addr=self.addr,
                loader=fake_load_source)

        self.assertEqual(self.plugin.loadedTestsFromName, True)
        self.assertEqual(result, "call")

    def test_loadTestsFromName_badsyntax(self):
        """Test loading by name when the script raises a SyntaxError."""
        self.addr.filename = "a path"
        self.addr.call = "call"

        def fake_load_bad_source(name, path):
            raise SyntaxError()

        result = self.plugin.loadTestsFromName("foo", addr=self.addr,
                loader=fake_load_bad_source)

        self.assertEqual(self.plugin.loadedTestsFromName, False)
        self.assertEqual(result, None)

    def test_loadTestsFromName_nofilename(self):
        """Test loading by name when the file has no filename."""
        self.addr.filename = ""

        result = self.plugin.loadTestsFromName("foo", addr=self.addr)

        self.assertEqual(result, None)

    def test_loadTestsFromName_secondtime(self):
        """Test repeatedly loading by name."""
        self.plugin.loadedTestsFromName = True
        result = self.plugin.loadTestsFromName("foo")

        self.assertEqual(result, None)

    def test_loadTestsFromName_module(self):
        """Test loading by name from a regular old module."""
        result = self.plugin.loadTestsFromName("foo", module="a module")

        self.assertEqual(result, None)

    def test_loadTestsFromName_notaname(self):
        """Test loading by a name that's not actually a name."""
        result = self.plugin.loadTestsFromName("foo")

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
    
    def test_load_source_script(self):
        """Test loading a script (sans .py extension)."""
        src = self.data("script")
        
        result = self.load_source("script", src)

        self.assertEqual(result.__name__, "script")
        self.assertEqual(result.__file__, src)
        self.assertEqual(inspect.getfile(result.test_bar), src)
        self.assertEqual(os.listdir(self.tmpdir), [os.path.basename(src)])
    
    def test_load_source_badscript(self):
        """Test loading a broken script."""
        src = self.data("badscript")
        
        self.assertRaises(SyntaxError, self.load_source, "badscript", src)
    
    def test_load_source_notascript(self):
        """Test loading something that isn't a script at all."""
        src = self.data("notascript")
        
        self.assertRaises(SyntaxError, self.load_source, "notascript", src)

class TestFunctional(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.processes = []
        self.env = {
                "PATH": os.environ["PATH"],
                "LANG": "C",
        }
        self.tmpdir = tempfile.mkdtemp(prefix="scriptloader-test-")
        self.oldcwd = os.getcwd()

        log.debug("Initializing test directory %r", self.tmpdir)
        os.chdir(self.tmpdir)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        log.debug("Cleaning up test directory %r", self.tmpdir)
        shutil.rmtree(self.tmpdir)
        os.chdir(self.oldcwd)

        for process in self.processes:
            log.debug("Reaping test process with PID %d", process.pid)
            try:
                process.kill()
            except OSError, e:
                if e.errno != 3:
                    raise

    def data(self, name):
        src = os.path.join(TESTDATA, name)
        dst = os.path.join(self.tmpdir, name)
        shutil.copy(src, dst)

        return dst

    def nose(self, *args, **kwargs):
        _args = ["nosetests", "--with-scriptloader"] + list(args)
        _kwargs = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "env": self.env,
        }
        communicate = kwargs.pop("communicate", True)
        _kwargs.update(kwargs)
        args = _args
        kwargs = _kwargs
        log.debug("Creating test process %r, %r", args, kwargs)
        process = subprocess.Popen(args, **kwargs)

        if communicate is True:
            stdout, stderr = process.communicate()
            process = (process, stdout, stderr)

        return process

    def test_plugin(self):
        """Check that the plugin is registered."""
        proc, stdout, stderr = self.nose("-p")

        self.assertTrue("Plugin scriptloader" in stdout)

    def test_script(self):
        """Run tests from a script."""
        src = self.data("script")
        proc, stdout, stderr = self.nose(src)

        self.assertEqual(stdout, "")
        self.assertTrue("Ran 2 tests" in stderr)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(os.listdir(self.tmpdir), [os.path.basename(src)])

    def test_script_name(self):
        """Run a test by name within a script."""
        src = self.data("script")
        proc, stdout, stderr = self.nose("%s:test_bar" % src)

        self.assertEqual(stdout, "")
        self.assertTrue("Ran 1 test" in stderr)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(os.listdir(self.tmpdir), [os.path.basename(src)])

    def test_badscript(self):
        """Try running a bad script."""
        src = self.data("badscript")
        proc, stdout, stderr = self.nose("%s" % src)

        self.assertEqual(stdout, "")
        self.assertTrue("Unable to load tests from file" in stderr)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(os.listdir(self.tmpdir), [os.path.basename(src)])

    def test_notascript(self):
        """Try running something that's not a script at all."""
        src = self.data("notascript")
        proc, stdout, stderr = self.nose("%s" % src)

        self.assertEqual(stdout, "")
        self.assertTrue("Unable to load tests from file" in stderr)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(os.listdir(self.tmpdir), [os.path.basename(src)])

    def test_module(self):
        """Test a module."""
        src = self.data("amodule.py")
        proc, stdout, stderr = self.nose("%s" % src)

        self.assertEqual(stdout, "")
        self.assertTrue("Ran 3 tests" in stderr)
        self.assertEqual(proc.returncode, 0)
        basename = os.path.basename(src)
        self.assertEqual(sorted(os.listdir(self.tmpdir)), [basename, basename + "c"])
