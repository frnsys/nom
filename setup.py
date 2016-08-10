from setuptools import setup

setup(
    name='nom',
    version='1.0.0',
    description='tool for managing markdown notes',
    url='https://github.com/frnsys/nom',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='GPLv3',

    packages=['nom'],
    install_requires=open('requirements.txt', 'r').readlines(),
    entry_points='''
        [console_scripts]
        nom=nom.cli:cli
    ''',
)