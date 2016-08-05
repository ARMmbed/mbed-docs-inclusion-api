import os, sys
from setuptools import setup


setup(
    name='api-inclusion',
    description='This is plugin to extend python markdown and allow it include api blocks from doxygen.',
    author='Michael Quested',
    author_email='michael.quested@arm.com',
    license='BSD',
    url='https://github.com/ARMmbed/mbed-docs/tree/master/readthedocs/mbed/markdown_extensions/api-inclusion',
    include_package_data=True,
    version='1.0',
    py_modules=['api_inclusion'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = ['markdown>=2.5'],
)
