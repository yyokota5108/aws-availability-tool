#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="aws_terraform_availability",
    version="0.1.0",
    description="Terraform可用性チェックツール",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/aws_availability_tool",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "terraform-availability=src.cli:main",
        ],
    },
    install_requires=[
        "boto3>=1.28.0",
        "rich>=13.0.0",
        "tfparse>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
    ],
) 