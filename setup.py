from setuptools import setup, find_packages

setup(
    name="compiler",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
