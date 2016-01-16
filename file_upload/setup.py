__author__ = 'ssinha'
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fileupload'))

long_description = '''
file_upload is a python query client that wraps the Oracle Rest API.
For uploading data into Oarcle,
'''

setup(
    name='fileupload',
    version= '0.0.1',
    author='Sandip Sinha',
    author_email='sandip.sinha@gmail.com',
    packages=['fileupload', 'fileupload.helper'],
    install_requires=[
        'requests',
    ],
    description='Wrapper to Oracle Rest API.',
    long_description=long_description
)
