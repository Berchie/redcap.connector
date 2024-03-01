import os
from setuptools import setup, find_packages
import sys

# add the path of the new different folder (the folder from where we want to import the modules)
sys.path.insert(0, f'{os.path.abspath(os.curdir)}/src')

setup(
    name='redcap-connector',
    version='1.1.0',
    author='Berchie Agyemang Nti',
    author_email='berchie@bnitm.de',
    packages=find_packages(),
    # py_modules=['redcap_connect','importdata','pull_data_senaite','senaite_connect','check_script'],
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'notify2',
        'pandas',
        'python-dotenv',
        'python-dateutil',
        'PyYAML',
        'urllib3'
    ],
    entry_points={
        'console_scripts': [
            'redcap-connector=src.main:cli'
        ],
    }
)
