from __future__ import with_statement

import sys

try:
    from setuptools import setup
    with_setuptools = True
except ImportError:
    from distutils.core import setup
    with_setuptools = False

with open('README.rst') as f:
    readme_content = f.read()

# version 2.5, 2.6 and 3.0 need the 3rd party package ordereddict
py_version = sys.version_info[:2]
needs_ordereddict = py_version in set([(2, 5), (2, 6), (3, 0)])

extra = {}
if with_setuptools:
    extra['install_requires'] = ['ordereddict'] if needs_ordereddict else []

setup(
    name='befungeshell',
    version='0.1b',
    author='Simon Liedtke',
    author_email='liedtke.simon@googlemail.com',
    url='https://github.com/derdon/befungeshell',
    description=(
        'An interactive shell for the esoteric programming language '
        'Befunge for debugging purposes.'),
    long_description=readme_content,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development'],
    py_modules=['befunge_shell'],
    scripts=['befunge_shell.py'],
    **extra
)
