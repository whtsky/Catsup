from setuptools import setup, find_packages

import catsup

version = catsup.__version__
long_description = open('README.rst').read().replace("develop", "master")
long_description = long_description.replace("latest", "v%s" % version)

setup(
    name='catsup',
    version=version,
    author='whtsky',
    author_email='whtsky@me.com',
    url='https://github.com/whtsky/Catsup',
    packages=find_packages(),
    description='Catsup: a lightweight static site generator',
    keywords="catsup, blog, site, static, static blog, static site, generator",
    long_description=long_description,
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
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
)
