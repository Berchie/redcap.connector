from setuptools import setup, find_packages

setup(
    name='redcap-connector',
    version='1.2.0',
    author='Berchie Agyemang',
    author_email='berchie@bnitm.de',
    description='Middleware for transferring analysis results from LIMS to REDCap',
    python_requires='>=3.10',
    packages=find_packages(
        include=[
            'redcapconnector',
            'redcapconnector.*',
            'redcapconnector/config',
            'redcapconnector/data',
            'redcapconnector/data/csv',
            'redcapconnector/data/daily_result',
            'redcapconnector/log'
        ],
        exclude=['src', 'src/*']
    ),
    py_modules=[
        'redcapconnector.main',
        'redcapconnector.check_status',
        'redcapconnector.extract_redcap_data',
        'redcapconnector.functions',
        'redcapconnector.importdata',
        'redcapconnector.pull_data_senaite',
        'redcapconnector.senaite_connect',
        'redcapconnector.sendemail'],
    include_package_data=True,
    install_requires=[
        'click>=8.1.7',
        'requests>=2.31.0',
        'notify2>=0.3.1',
        'dbus-python>=1.3.2',
        'python-dotenv>=1.0.1',
        'python-dateutil>=2.9.0.post0',
        'PyYAML>=6.0.1',
        'tqdm>=4.66.2',
        'loguru>=0.7.2',
        'loguru-config>=0.1.0'
    ],
    entry_points={
        'console_scripts': [
            'redcon=redcapconnector.main:cli'
        ]
    }

)
