#! /usr/bin/python3
# -*- coding:Utf-8 -*-

from setuptools import setup

files = ["images/*"]

setup(name = "FolderSync",
	  version = "1.0.8",
	  description = "Folder synchronisation software",
	  author = "Juliette Monsel",
	  author_email = "j_4321@protonmail.fr",
	  license = "GNU General Public License v3",
	  packages = ['foldersynclib'],
	  package_data = {'foldersynclib' : files },
	  data_files = [("share/pixmaps", ["foldersync.svg"]),
					("share/applications", ["foldersync.desktop"])],
	  scripts = ["foldersync"],
	  long_description = """FolderSync is a utility to keep your backups up to date. You can visualise the differences between your data and your backup and choose what will be copied and what will be suppressed. The frequent synchronisation paths can be saved as favorites.""",
	  requires = ["os", "sys", "subprocess", "threading", "queue", "tkinter",
                  "configparser"]
)
