import os
from os.path import join, dirname, split
#from distutils.core import setup
from setuptools import setup, find_packages


with open('requirements.txt', 'r') as f:
    requirements = f.readlines()


setup(
    name='raccbot_client',
    version='1.0',
    description='Client for telegram bot edX installations',
    author='edX',
    url='https://github.com/raccoongang/raccbot_client',
    
    install_requires=requirements,
    packages=find_packages(exclude=[]),
)
