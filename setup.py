from setuptools import setup
import os
version = '0.3.1dev'

# Copy default config if not exists

if not os.path.isdir('/home/pi/raspi-sump'):
    cmds = ('mkdir /home/pi/raspi-sump/',
            'cp conf/raspisump.conf /home/pi/raspi-sump/',
            'mkdir /home/pi/raspi-sump/charts/',
            'mkdir /home/pi/raspi-sump/logs/',
            'mkdir /home/pi/raspi-sump/csv/',
            'mkdir /home/pi/raspi-sump/docs/',
            'cp docs/* /home/pi/raspi-sump/docs/',
            'chown -R pi /home/pi/raspi-sump/'
            )
    for cmd in cmds:
        os.system(cmd)
else:
    cmds = ('cp -u docs/* /home/pi/raspi-sump/docs',
            'chown -R pi /home/pi/raspi-sump/'
            )
    for cmd in cmds:
        os.system(cmd)

raspi_sump_files = ['raspisump/raspisump.py',
                    'raspisump/raspisump_alternate.py',
                    'raspisump/todaychart.py',
                    'raspisump/checkpid.py'
                    ]

config = {
    'name': 'Raspi-Sump',
    'description': 'A sump pit monitoring system for Raspberry Pi',
    'author': 'Al Audet',
    'author_email': 'alaudet@linuxnorth.org.',
    'url': 'http://www.linuxnorth.org/raspi-sump/',
    'download_url': 'https://github.com/alaudet/raspi-sump/releases',
    'version': version,
    'license': 'MIT License',
    'install_requires': ['RPi.GPIO'],
    'scripts': raspi_sump_files
}

setup(**config)
