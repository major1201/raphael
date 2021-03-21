# encoding: utf-8

from setuptools import find_packages, setup


setup(
    name='raphael',
    version='0.1.0',
    python_requires='>=3.4',
    url='https://github.com/major1201/raphael',
    author='major1201',
    author_email='major1201@gmail.com',
    description='Raphael, an OpenLDAP management system',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'APScheduler==3.5.1',
        'asn1crypto==0.24.0',
        'certifi==2018.4.16',
        'cffi==1.11.5',
        'chardet==3.0.4',
        'click==6.7',
        'cryptography==3.2',
        'Flask==1.0.2',
        'future==0.16.0',
        'geoip2==2.9.0',
        'idna==2.7',
        'itsdangerous==0.24',
        'Jinja2==2.11.3',
        'ldap3==2.5.1',
        'MarkupSafe==1.0',
        'maxminddb==1.4.1',
        'pyasn1==0.4.4',
        'pycparser==2.18',
        'pycrypto==2.6.1',
        'PyMySQL==0.9.2',
        'pyotp==2.2.6',
        'PyQRCode==1.2.1',
        'python-memcached==1.59',
        'pytz==2018.5',
        'PyYAML>=4.2b1',
        'requests==2.21.0',
        'six==1.11.0',
        'SQLAlchemy==1.3.0',
        'tzlocal==1.5.1',
        'urllib3==1.24.2',
        'uWSGI==2.0.17.1',
        'Werkzeug==0.15.3',
    ],
    extras_require={}
)
