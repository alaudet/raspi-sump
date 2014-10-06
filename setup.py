from setuptools import setup
import os
version = '0.3.1dev'

# Copy default config if not exists
raspi_sump_dir = '/home/pi/raspi-sump/'
conf_path = '{}raspisump.conf'.format(raspi_sump_dir)
chart_path = '{}charts/'.format(raspi_sump_dir)
log_path = '{}logs/'.format(raspi_sump_dir)
csv_path = '{}csv/'.format(raspi_sump_dir)
docs_path = '{}docs/'.format(raspi_sump_dir)
if os.path.isdir(raspi_sump_dir):
    print 'Updating install document for version {}'.format(version)
    cmd = 'cp -u docs/*.md ' + docs_path
    os.system(cmd)
    cmd = 'chown -R pi ' + raspi_sump_dir
    os.system(cmd)
else:
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
    cmd = 'chown -R pi ' + raspi_sump_dir
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
    'install_requires': ['RPi.GPIO'],
    'scripts': raspi_sump_files
}

setup(**config)


print ''
print "*************************************************************"
print "*See /home/pi/raspi-sump/docs for configuration information.*"
print "*************************************************************"
print ''
