from setuptools import setup

version = "1.11.1"

raspi_sump_files = [
    "bin/rsump.py",
    "bin/rsumpchart.py",
    "bin/rsumpmonitor.py",
    "bin/rsumpwebchart.py",
    "bin/alerttest",
    "bin/rsumpsupport",
]

add_files = [
    ("/etc/raspi-sump", ["conf/raspisump.conf"]),
    ("/usr/share/raspi-sump/web", ["conf/web/index.html"]),
    ("/usr/share/raspi-sump/web/images", ["conf/web/images/logo.png"]),
    ("/usr/share/raspi-sump/web/css", ["conf/web/css/index.html"]),
    ("/usr/share/raspi-sump/web/css", ["conf/web/css/raspi.css"]),
    ("/usr/share/raspi-sump/web/css", ["conf/web/css/includes.js"]),
    ("/usr/share/raspi-sump/web/css/inc", ["VERSION"]),
    ("/usr/share/doc/raspi-sump", ["README.md", "VERSION", "LICENSE"]),
    ("/usr/share/doc/raspi-sump", ["docs/README.md", "docs/install.md"]),
    ("/lib/systemd/system", [
        "conf/systemd/raspisump.service",
        "conf/systemd/rsumpwebchart.service",
        "conf/systemd/rsumpwebchart.timer",
    ]),
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.11",
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
    install_requires=["hcsr04sensor>=1.7", "Mastodon.py"],
)
