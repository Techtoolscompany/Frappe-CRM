from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in church_management/__init__.py
from church_management import __version__ as version

setup(
    name="church_management",
    version=version,
    description="A comprehensive church management system",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
