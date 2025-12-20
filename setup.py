from setuptools import setup, find_packages

setup(
    name="qt_common",
    version="3.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6>=6.0.0",
        "peewee",
    ],
    python_requires=">=3.6",
) 