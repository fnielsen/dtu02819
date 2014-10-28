import os
from setuptools import setup


setup(
    name='dtu02819',
    version='0.1',
    author='Finn Aarup Nielsen',
    author_email='faan@dtu.dk',
    description='Handle course information from DTU course 02819',
    license='GPL',
    keywords='course',
    url='https://github.com/fnielsen/dtu02819',
    py_modules=['dtu02819'],
    long_description='',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        ],
    tests_require=['pytest'],
    test_suite='py.test',
    )
