import unittest

def test_bar():
    pass

class TestFoo(unittest.TestCase):

    def test_foo(self):
        pass

if __name__ == "__main__":
    import sys
    spam = "eggs"
    sys.exit(0)

class TestBar(unittest.TestCase):

    def test_bar(self):
        pass
