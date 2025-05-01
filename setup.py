"""wutils: handy tools
"""
import subprocess
from codecs import open
from os import path

from setuptools import Command, find_packages, setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line]

setup(
    name="xagents",
    version="0.1",
    description="A Framework for Interpretable Rule-Based Multi-Agents Cooperation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AGI-FHBC/XAgents",
    author="Mingxian Gu",
    author_email="gumingxian@stu.jiangnan.edu.cn",
    license="Apache 2.0",
    packages=find_packages(exclude=["contrib", "docs", "examples"]),
    python_requires=">=3.10",
    install_requires=requirements,
)
