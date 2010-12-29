import sys

from setuptools import setup

meta = dict(
    name="scriptloader",
    version="0.2.0",
    description="scriptloader loads scripts (into nose)",
    author="Will Maier",
    author_email="willmaier@ml1.net",
    py_modules=["scriptloader"],
    test_suite="tests",
    install_requires=["setuptools"],
    keywords="nose testing scripts",
    url="http://packages.python.org/scriptloader",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
    entry_points = {
        'nose.plugins.0.10': [
            'scriptloader = scriptloader:ScriptLoader'
        ]
    },
)

# Automatic conversion for Python 3 requires distribute.
if False and sys.version_info >= (3,):
    meta.update(dict(
        use_2to3=True,
    ))

setup(**meta)
