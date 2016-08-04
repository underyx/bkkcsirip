import io
from setuptools import setup

with io.open('README.md', encoding='utf-8') as f:
    README = f.read()

setup(
    name='bkkcsirip',
    version='1.1.0',
    url='https://github.com/underyx/bkkcsirip',
    author='Bence Nagy',
    author_email='bence@underyx@me',
    maintainer='Bence Nagy',
    maintainer_email='bence@underyx.me',
    download_url='https://github.com/underyx/bkkcsirip/releases',
    long_description=README,
    py_modules=['bkkcsirip'],
    package_data={'': ['LICENSE']},
    install_requires=[
        'arrow<0.9',
        'oauthlib<2',
        'redis<3',
        'requests<3',
        'requests-oauthlib<0.6',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ]
)
