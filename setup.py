#!/usr/bin/env python
import cython_npm
from setuptools import setup, find_packages

# python setup.py sdist bdist_wheel
# twine upload dist/*

# I really prefer Markdown to reStructuredText.  PyPi does not.  This allows me
# to have things how I'd like, but not throw complaints when people are trying
# to install the package and they don't have pypandoc or the README in the
# right place.
readme=''
try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   readme = ''


setup(
    name='cython_npm',
    version='0.1.7',
    description='Cython project management like npm in nodejs',
    long_description=readme,
    author=cython_npm.__author__,
    author_email='ntuan221@gmail.com',
    license='MIT',
    platforms=['POSIX'],
    url='https://github.com/minhtuan221/cython-npm',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',],
    # entry_points={'console_scripts': [
    #     'cython_npm = cython_npm:main',
    # ]},
    packages=find_packages(exclude=('test*','testpandoc*' )),
    include_package_data=False,
    install_requires=['cython>=0.27.3'],
)

