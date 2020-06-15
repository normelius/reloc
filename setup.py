import setuptools
from distutils.util import convert_path

NAME = "reloc"
AUTHOR = "Anton Normelius"
EMAIL = "a.normelius@gmail.com"
DESCRIPTION = "Package for simple file transfer between client and server"
URL = "https://github.com/normelius/reloc"
PACKAGES = ['reloc']
PYTHON_REQUIRES = ">=3.6"


with open("README.md", "r") as fh:
    long_description = fh.read()

# Read latest version
VER = {}
version_path = convert_path("reloc/__version__.py")
with open(version_path) as version_file:
    exec(version_file.read(), VER)


setuptools.setup(
    name=NAME,
    version=VER['__version__'],
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=PYTHON_REQUIRES,
    entry_points = {
        'console_scripts': ['reloc=reloc.cli:cli_transmit'],
    }
)
