import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-globee',
    version='1.3.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A Django app for integrating Globee Payments',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/lovvskillz/django-globee',
    install_requires=[
            'Django>=2.0',
            'six>=1.4.1',
            'requests>=2.19.1',
            'pytz>=2018.5',
    ],
    author='Vadim Zifra',
    author_email='vadim@minehub.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
