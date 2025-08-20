from setuptools import find_packages, setup

setup(
    packages=find_packages(),
    extras_require={
        "dev": [
            "pre-commit>=3.5.0",
            "ruff>=0.8.5",
        ],
    },
)
