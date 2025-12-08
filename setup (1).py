"""
RoboKen Simulator - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="roboken-simulator",
    version="1.0.0",
    author="RoboKen Development Team",
    author_email="dev@roboken.ai",
    description="PC & Smartphone Operation Learning Simulator with AI-Powered Task Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robokenjp/roboken-simulator",
    project_urls={
        "Bug Tracker": "https://github.com/robokenjp/roboken-simulator/issues",
        "Documentation": "https://docs.roboken.ai",
        "Source Code": "https://github.com/robokenjp/roboken-simulator",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.12.0",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.14",
        ],
    },
    entry_points={
        "console_scripts": [
            "roboken=roboken_complete_platform:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "automation",
        "ai",
        "machine-learning",
        "task-automation",
        "workflow",
        "robotic-process-automation",
        "rpa",
        "nlp",
        "computer-vision",
    ],
)
