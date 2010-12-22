import sys

from setuptools import setup

meta = dict(
    name="nose-script",
    version="0.1.0",
    description="load nose tests from scripts without the .py extension",
    author="Will Maier",
    author_email="willmaier@ml1.net",
    py_modules=["nosescript"],
    test_suite="tests",
    install_requires=["setuptools"],
    keywords="nose testing scripts",
    url="http://packages.python.org/nosescript",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
)

# Automatic conversion for Python 3 requires distribute.
if False and sys.version_info >= (3,):
    meta.update(dict(
        use_2to3=True,
    ))

setup(**meta)
