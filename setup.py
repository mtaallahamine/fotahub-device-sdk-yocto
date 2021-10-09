from setuptools import setup, find_packages

# Prerequisites: sudo apt-get install pkg-config libcairo2-dev gcc python3-dev libgirepository1.0-dev

setup(
    name='fotahubclient',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'gobject',
        'PyGObject',
        'pydbus',
        'stringcase',
    ],
    entry_points='''
        [console_scripts]
        fotahub=fotahubclient.cli.main:main
    ''',
)