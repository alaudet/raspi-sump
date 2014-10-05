from setuptools import setup
import os
version = '0.2.1'

# Copy default config if not exists
raspi_sump_dir = '/home/pi/raspi-sump/'
conf_path = '/home/pi/raspi-sump/raspisump.conf'
chart_path = '/home/pi/raspi-sump/charts/'
log_path = '/home/pi/raspi-sump/logs/'
csv_path = '/home/pi/raspi-sump/csv/'
docs_path = '/home/pi/raspi-sump/docs/'
if not os.path.isdir(raspi_sump_dir):
    cmd = 'mkdir ' + raspi_sump_dir
    os.system(cmd)
    cmd = 'cp conf/raspisump.conf ' + conf_path
    os.system(cmd)
    cmd = 'chmod 700 ' + conf_path
    os.system(cmd)
    cmd = 'mkdir ' + chart_path
    os.system(cmd)
    cmd = 'mkdir ' + log_path
    os.system(cmd)
    cmd = 'mkdir ' + csv_path
    os.system(cmd)
    cmd = 'mkdir ' + docs_path
    os.system(cmd)
    cmd = 'cp docs/README.md ' + docs_path
    os.system(cmd)
else:
    pass

config = {
    'description': 'Raspi-Sump',
    'author': 'Al Audet',
    'url': 'http://www.linuxnorth.org',
    'download_url': 'http://www.linuxnorth.org',
    'author_email': 'audet@linuxnorth.org.',
    'version': version,
    'install_requires': ['RPi.GPIO'],
    'packages': ['raspisump'],
    'scripts': [],
    'name': 'Raspi-Sump'
}

setup(**config)
print ""
print "*************************************************************"
print "*See /home/pi/raspi-sump/docs for configuration information.*"
print "*************************************************************"
print ""

