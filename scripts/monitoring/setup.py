"""
DiveTeacher Monitoring Suite Setup

Installation:
    pip install -e scripts/monitoring
"""

from setuptools import setup, find_packages


setup(
    name="diveteacher-monitor",
    version="1.0.0",
    description="Monitoring and management tools for DiveTeacher RAG System",
    author="DiveTeacher Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "httpx>=0.25.0",
    ],
    entry_points={
        'console_scripts': [
            'diveteacher-monitor=cli:cli',
        ],
    },
    python_requires='>=3.11',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)

