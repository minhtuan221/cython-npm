#!/usr/bin/env python
import cython_npm
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

def install():

    setup(
        name='cython_npm',
        version=cython_npm.__version__,
        description='Create flask web apps with directory layout',
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
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',],
        # entry_points={'console_scripts': [
        #     'cython_npm = cython_npm:main',
        # ]},
        packages=find_packages(exclude=('test*', )),
        include_package_data=False,
        install_requires=['cython'],
    )

if __name__ == "__main__":
    install()