from setuptools import find_packages, setup

setup(
    name="perpetual",
    version="0.1.0",
    packages=find_packages(
        include=[
            "pipeline",
            "pipeline.*",
        ]
    ),
    install_requires=[],
)
