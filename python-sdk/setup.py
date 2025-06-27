#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pleom-apitoolbox",
    version="1.0.0",
    author="Royce Arockiasamy",
    author_email="royce@pleom.com",
    description="Stateless API Mapping Context for LLM Tooling - Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pleom/apitoolbox",
    project_urls={
        "Bug Tracker": "https://github.com/pleom/apitoolbox/issues",
        "Homepage": "https://apitoolbox.dev",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
        ],
    },
    keywords=[
        "api",
        "sdk",
        "python",
        "tools",
        "llm",
        "ai",
        "async"
    ],
    include_package_data=True,
    zip_safe=False,
) 