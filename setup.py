from setuptools import setup, find_packages

import catsup

setup(
    name='catsup',
    version=catsup.__version__,
    author='whtsky',
    author_email='whtsky@me.com',
    url='https://github.com/whtsky/catsup',
    packages=find_packages(),
    description='Catsup: a lightweight static site generator',
    long_description=open('README.rst').read(),
    entry_points={
        'console_scripts': ['catsup= catsup.cli:main'],
    },
    install_requires=open("requirements.txt").readlines(),
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
)
