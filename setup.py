#! /usr/bin/python3
# -*- coding:Utf-8 -*-

from setuptools import setup

with open('foldersynclib/version.py') as file:
    exec(file.read())

files = ["images/*"]

setup(name = "FolderSync",
	  version = __version__,
	  description = "Folder synchronisation software",
	  author = "Juliette Monsel",
	  author_email = "j_4321@protonmail.fr",
	  url = "https://github.com/j4321/FolderSync",
	  license = "GNU General Public License v3",
	  packages = ['foldersynclib'],
	  package_data = {'foldersynclib' : files },
	  data_files = [("share/locale/en_US/LC_MESSAGES/", ["foldersynclib/locale/en_US/LC_MESSAGES/FolderSync.mo"]),
					("share/locale/fr_FR/LC_MESSAGES/", ["foldersynclib/locale/fr_FR/LC_MESSAGES/FolderSync.mo"]),
	                ("/usr/share/pixmaps", ["foldersync.svg"]),
					("/usr/share/applications", ["foldersync.desktop"])],
	  scripts = ["foldersync"],
	  long_description = """FolderSync is a utility to keep your backups up to date. You can visualise the differences between your data and your backup and choose what will be copied and what will be suppressed. The frequent synchronisation paths can be saved as favorites.""",
	  install_requires = ["psutil"])
