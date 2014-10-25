from setuptools import setup
import os
version = '0.5.0'

homedir = '/home/pi/raspi-sump/'

if os.path.isfile(homedir + 'raspisump.conf'):
    cmd = 'cp -u ' + homedir + 'raspisump.conf ' + homedir + \
        'raspisump.conf.save'
    os.system(cmd)

raspi_sump_files = ['bin/rsump.py',
                    'bin/rsumpchart.py',
                    'bin/rsumpmonitor.py'
                    ]

add_files = [(homedir + 'sample_config', ['conf/raspisump.conf']),
             (homedir + 'csv', ['conf/csv/README.md']),
             (homedir + 'logs', ['conf/logs/README.md']),
             (homedir + 'charts', ['conf/charts/README.md']),
             (homedir + 'docs', ['docs/README.md']),
             (homedir + 'docs', ['docs/automated_install.md']),
             (homedir + 'simulations', ['simulations/README.md']),
             (homedir + 'simulations', ['simulations/sim-pump-fail.py']),
             (homedir + 'simulations', ['simulations/sim-pump-working.py']),
             (homedir + 'cron', ['cron/README.md']),
             (homedir + 'cron', ['cron/move_file.sh']),
             (homedir + 'cron', ['cron/picrontab']),
             ]

setup(name='raspisump',
      version=version,
      description='A sump pit monitoring system for Raspberry Pi',
      long_description=open("./README.md", "r").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2.7",
          "Topic :: Home Automation",
          "License :: OSI Approved :: MIT License",
          ],
      author='Al Audet',
      author_email='alaudet@linuxnorth.org',
      url='http://www.linuxnorth.org/raspi-sump/',
      download_url='https://github.com/alaudet/raspi-sump/releases',
      license='MIT License',
      packages=['raspisump'],
      scripts=raspi_sump_files,
      data_files=add_files,
      install_requires=['RPi.GPIO']
      )

if os.path.isdir(homedir):
    cmd = 'chown -R pi ' + homedir
    os.system(cmd)
    cmd = 'chmod 600 ' + homedir + 'raspisump.conf'
    os.system(cmd)
