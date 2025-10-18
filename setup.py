"""Setup script for SentinelDF CLI installation."""

from setuptools import find_packages, setup

setup(
    name="sentineldf",
    version="1.0.0",
    description="Data Firewall for LLM Training",
    author="SentinelDF Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.7",
        "fastapi>=0.95.2",
        "uvicorn>=0.22.0",
        "sentence-transformers>=2.2.2",
        "scikit-learn>=1.2.2",
        "pydantic>=1.10.12",
    ],
    entry_points={
        "console_scripts": [
            "sdf=cli.sdf:main",
        ],
    },
    python_requires=">=3.10",
)
