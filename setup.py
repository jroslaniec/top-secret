from setuptools import find_packages
from setuptools import setup

NAME = "top_secret"
VERSION = "0.2.0"
SUMMARY = "Small python library for getting secret from various places like environment variables or files."

setup(
    name=NAME,
    version=VERSION,
    description=SUMMARY,
    url="https://github.com/jroslaniec/top-secret",
    author="Jędrzej Rosłaniec",
    author_email="jedr.ros@gmail.com",
    license="MIT",
    test_suite="tests",
    install_requires=["PyYAML==5.1"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords=("secrets",),
    packages=find_packages(exclude=["examples", "docs", "tests*"]),
)
