from setuptools import setup
import os

version = "1.7"
user = os.getlogin()

homedir = "/home/" + user + "/raspi-sump/"

if os.path.isfile(homedir + "raspisump.conf"):
    cmd = "cp -u " + homedir + "raspisump.conf " + homedir + "raspisump.conf.save"
    os.system(cmd)

raspi_sump_files = [
    "bin/rsump.py",
    "bin/rsumpchart.py",
    "bin/rsumpmonitor.py",
    "bin/rsumpwebchart.py",
    "bin/emailtest",
]

add_files = [
    (homedir + "sample_config", ["conf/raspisump.conf"]),
    (homedir + "csv", ["conf/csv/README.md"]),
    (homedir + "logs", ["conf/logs/README.md"]),
    (homedir + "charts", ["conf/charts/README.md"]),
    (homedir + "docs", ["docs/README.md"]),
    (homedir + "docs", ["docs/install.md"]),
    (homedir + "cron", ["cron/README.md"]),
    (homedir + "cron", ["cron/picrontab"]),
    (homedir + "web", ["conf/web/index.html"]),
    (homedir + "web/images", ["conf/web/images/logo.png"]),
    (homedir + "web/css", ["conf/web/css/index.html"]),
    (homedir + "web/css", ["conf/web/css/raspi.css"]),
    (homedir, ["VERSION"])
]

setup(
    name="raspisump",
    version=version,
    description="A sump pit monitoring system for Raspberry Pi",
    long_description_content_type="text/markdown",
    long_description=open("./README.md", "r").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
    ],
    author="Al Audet",
    author_email="alaudet@linuxnorth.org",
    url="https://www.linuxnorth.org/raspi-sump/",
    download_url="https://github.com/alaudet/raspi-sump/releases",
    license="MIT License",
    packages=["raspisump"],
    scripts=raspi_sump_files,
    data_files=add_files,
    install_requires=["hcsr04sensor"],
)

if os.path.isdir(homedir):
    cmd = "chown -R " + user + " " + homedir
    os.system(cmd)
    cmd = "chmod 600 " + homedir + "raspisump.conf"
    os.system(cmd)
    cmd = "chmod 600 " + homedir + "sample_config/raspisump.conf"
    os.system(cmd)
