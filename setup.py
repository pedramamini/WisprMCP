"""
Setup configuration for WisprMCP.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wispr-mcp",
    version="0.1.0",
    author="Pedram",
    description="A Python library for accessing Wispr Flow's SQLite database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        # Zero external dependencies - using only Python standard library
    ],
    extras_require={
        "rich": ["rich>=10.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wispr=wispr_mcp.cli.main:main",
            "wispr-mcp=wispr_mcp.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Communications",
        "Topic :: Text Processing",
    ],
    keywords="wispr flow sqlite database transcripts conversations mcp",
    project_urls={
        "Bug Reports": "https://github.com/pedram/WisperMCP/issues",
        "Source": "https://github.com/pedram/WisperMCP",
    },
)