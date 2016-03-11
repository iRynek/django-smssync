import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-smssync',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='GNU GPLv3',
    description='A simple Django app to integrate with SMSSync, an SMS gateway for Android.',
    long_description=README,
    url='https://github.com/rodrigopitanga/django-smssync/',
    author='Rodrigo Pitanga',
    author_email='pitanga@members.fsf.org',
    install_requires=[
        'django-phonenumber-field',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU GPLv3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
