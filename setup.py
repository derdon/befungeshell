from distutils.core import setup

setup(
    name='befungeshell',
    version='0.1b',
    author='Simon Liedtke',
    author_email='liedtke.simon@googlemail.com',
    url='https://github.com/derdon/befungeshell',
    description=(
        'An interactive shell for the esoteric programming language '
        'Befunge for debugging purposes.'),
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
)
