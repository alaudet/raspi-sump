try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Raspi-Sump',
    'author': 'Al Audet',
    'url': 'https://github.com/alaudet/raspi-sump-monitor',
    'download_url': 'Where to download it.',
    'author_email': 'alaudet@linuxnorth.org.',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'raspi-sump-monitor'
}

setup(**config)
