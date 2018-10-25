#! /usr/bin/python3
# -*- coding:Utf-8 -*-

from setuptools import setup
from sys import platform
import os


with open('foldersynclib/version.py') as file:
    exec(file.read())

if platform.startswith('linux'):
    images = [os.path.join("foldersynclib/images/", img) for img in os.listdir("foldersynclib/images/")]
    files = []
    data_files = [("/usr/share/locale/en_US/LC_MESSAGES/", ["foldersynclib/locale/en_US/LC_MESSAGES/FolderSync.mo"]),
                  ("/usr/share/locale/fr_FR/LC_MESSAGES/", ["foldersynclib/locale/fr_FR/LC_MESSAGES/FolderSync.mo"]),
                  ("/usr/share/foldersync/images/", images),
                  ("/usr/share/doc/foldersync/", ["README.rst", 'changelog']),
                  ("/usr/share/man/man1", ["foldersync.1.gz"]),
                  ("/usr/share/pixmaps", ["foldersync.svg"]),
                  ("/usr/share/applications", ["foldersync.desktop"])]
else:
    files = ["images/*", "locale/en_US/LC_MESSAGES/*", "locale/fr_FR/LC_MESSAGES/*"]
    data_files = []
    
setup(name="FolderSync",
	  version=__version__,
	  description="Folder synchronisation software",
	  author="Juliette Monsel",
	  author_email="j_4321@protonmail.fr",
	  url="https://github.com/j4321/FolderSync",
	  license="GNU General Public License v3",
	  packages=['foldersynclib'],
	  package_data={'foldersynclib' : files},
	  data_files=data_files,
	  scripts=["foldersync"],
	  long_description="""FolderSync is a utility to keep your backups up to date. You can visualise the differences between your data and your backup and choose what will be copied and what will be suppressed. The frequent synchronisation paths can be saved as favorites.""")
