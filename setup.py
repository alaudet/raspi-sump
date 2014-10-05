from setuptools import setup
import os
version = '0.2.1'

# Copy default config if not exists
raspi_sump_dir = '/home/pi/raspi-sump/'
conf_path = '{}raspisump.conf'.format(raspi_sump_dir)
chart_path = '{}charts/'.format(raspi_sump_dir)
log_path = '{}logs/'.format(raspi_sump_dir)
csv_path = '{}csv/'.format(raspi_sump_dir)
docs_path = '{}docs/'.format(raspi_sump_dir)
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
    print 'Updating install document for version {}'.format(version)
    cmd = 'cp -u docs/README.md ' + docs_path  
    os.system(cmd)

config = {
    'description': 'Raspi-Sump',
    'author': 'Al Audet',
    'url': 'http://www.linuxnorth.org/raspi-sump/',
    'download_url': 'https://github.com/alaudet/raspi-sump/releases',
    'author_email': 'alaudet@linuxnorth.org.',
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