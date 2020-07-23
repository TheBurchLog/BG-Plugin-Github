import re

from setuptools import setup


def find_version(version_file):
    version_line = open(version_file, "rt").read()
    match_object = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line, re.M)

    if not match_object:
        raise RuntimeError("Unable to find version string in %s" % version_file)

    return match_object.group(1)


setup(
    name="github_summary",
    version=find_version("github_summary/__main__.py"),
    description="A plugin that will create summaries of Github Repos/Organizations",
    url="https://beer-garden.io",
    author="TheBurchLog",
    author_email=" ",
    license="MIT",
    packages=["github_summary"],
    install_requires=["brewtils", "pygithub"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
