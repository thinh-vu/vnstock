import os
import shutil
import subprocess
from setuptools import setup, find_packages, Command
from setuptools.command.install import install

setup(
    name="vnstock",
    version="3.2.3",
    description="A comprehensive and transparent solution for Vietnamese stock market analysis.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Thinh Vu",
    author_email="support@vnstocks.com",
    url="https://github.com/thinh-vu/vnstock",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    packages=find_packages(),
    package_data={
        "vnstock": ["docs/*.txt", "docs/*.csv"],
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "seaborn",
        "vnai>=2.0.1",
        "openpyxl",
        "pydantic",
        "psutil",
        "fake_useragent",
        "vnstock_ezchart",
        "click",
        "packaging>=20.0",
        "importlib-metadata>=1.0",
        "tenacity",
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
    entry_points={
        'console_scripts': [
            'vnstock=vnstock.common.cli:cli',
        ],
    },
)
