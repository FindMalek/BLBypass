from setuptools import setup, find_packages

setup(
    name="blbypass",
    version="0.1.0",
    description="CLI tool to automate BlackLight 3 trial extension requests",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pyperclip>=1.8.2",
        "click>=8.1.7",
        "rich>=13.7.0",
        "python-dateutil>=2.8.2",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "blbypass=blbypass.cli:main",
        ],
    },
    python_requires=">=3.8",
)