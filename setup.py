import os
import shutil
import subprocess
from setuptools import setup, find_packages, Command
from setuptools.command.install import install

setup(
    name="vnstock3",
    version="0.3.0.4",
    description="A comprehensive and transparent solution for Vietnamese stock market analysis.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Thinh Vu",
    author_email="mrthinh@live.com",
    url="https://github.com/thinh-vu/vnstock",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    packages=find_packages(),
    package_data={
        "vnstock3": ["docs/*.txt", "docs/*.csv"],
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "vnai>=0.1.0",
        "openpyxl",
        "pydantic",
        "psutil",
        "fake_useragent",
        "vnstock_ezchart"
     ],
    extras_require={
        "dev": ["flake8"],
        "docs": ["sphinx", "sphinx_rtd_theme"],
        "test": ["unittest"],
    },
    setup_requires=[
        "setuptools>=42",
        "wheel",
    ],
)
