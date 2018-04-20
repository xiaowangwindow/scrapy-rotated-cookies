
from distutils.core import setup

from setuptools import find_packages

setup(
    name='scrapy-rotated-cookies',
    version='0.0.1',
    author='alex-wang',
    description='A Scrapy middleware to attach cookie to request rotatedly',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
)
