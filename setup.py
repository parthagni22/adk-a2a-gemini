"""Setup script for ADK A2A Gemini project."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="adk-a2a-gemini",
    version="1.0.0",
    description="ADK A2A Multi-Agent System with Gemini, Notion, and ElevenLabs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/adk-a2a-gemini",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=25.1.0",
            "isort>=5.13.0",
            "mypy>=1.16.0",
            "flake8>=7.0.0",
        ]
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "adk-agents=scripts.start_agents:main",
            "adk-test=scripts.test_setup:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)