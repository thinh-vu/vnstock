import os
import shutil
import subprocess
from setuptools import setup, find_packages, Command
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vnstock",
    version="3.2.7",
    description="A beginner-friendly yet powerful Python toolkit for financial analysis and automation — built to make modern investing accessible to everyone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Thinh Vu",
    author_email="support@vnstocks.com",
    url="https://github.com/thinh-vu/vnstock",
    project_urls={
        "Documentation": "https://github.com/thinh-vu/vnstock",
        "Source": "https://github.com/thinh-vu/vnstock",
        "Issue Tracker": "https://github.com/thinh-vu/vnstock/issues",
    },
    keywords="vnstock, finance, vietnam, stock market, analysis, API",
    license="Custom: Personal, research, non-commercial; contact support@vnstocks.com for other use",
    classifiers=[
        # Trạng thái phát triển
        "Development Status :: 5 - Production/Stable",
        # Đối tượng sử dụng
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        # Lĩnh vực
        "Topic :: Software Development :: Libraries",
        "Topic :: Office/Business :: Financial :: Investment",
        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        # Hệ điều hành
        "Operating System :: OS Independent",
        # License (custom)
        "License :: Other/Proprietary License",
        # Ngôn ngữ tự nhiên của package
        "Natural Language :: English",
        "Natural Language :: Vietnamese",
    ],
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests*", "docs*"]),
    include_package_data=True,
    package_data={
        "vnstock": ["docs/*.txt", "docs/*.csv"],
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "seaborn",
        "openpyxl",
        "pydantic",
        "psutil",
        "fake_useragent",
        "vnstock_ezchart",
        "click",
        "packaging>=20.0",
        "importlib-metadata>=1.0",
        "tenacity",
        "vnai>=2.0.3",
        # "vnai @ https://github.com/vnstock-hq/initialization/releases/download/vnai-2.0.3/vnai-2.0.3.tar.gz"
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
