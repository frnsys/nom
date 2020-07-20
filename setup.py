from setuptools import setup

setup(
    name='nom',
    version='1.4.0',
    description='tool for managing markdown notes',
    package_data={'': ['templates/*']},
    include_package_data=True,
    url='https://github.com/frnsys/nom',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='GPLv3',

    packages=['nom'],
    install_requires=[
        'Jinja2==2.8',
        'Markdown==2.6.5',
        'click==6.2',
        'gfm==0.0.3',
        'lxml==4.5.2',
        'html2text==2015.11.4',
        'py-gfm==0.1.1',
        'watchdog==0.8.3',
        'Pygments==2.1.3',
        'websocket-server==0.4',
        'requests==2.24.0'
    ],
    entry_points='''
        [console_scripts]
        nom=nom.cli:cli
    ''',
)
