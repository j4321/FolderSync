FolderSync
==========
Folder synchronisation software
-------------------------------

Copyright (C) 2016-2018  Juliette Monsel <j_4321@protonmail.com>

Prerequisite
------------

This software was designed for linux and requires the system commands ``cp -ra --parent`` and ``rm -r``.
It also depends on the Tkinter library for the GUI, so tcl/tk should be installed (`python3-tk` package for Ubuntu users)

Optional dependencies:

    * zenity or tkfilebrowser: nicer file dialogs
    * libnotify and a notification server if your desktop environment does not provide one: to be notified when the scan/sync is finished 

Install
-------

    ::

        $sudo python3 setup.py install

Run without installing
----------------------

    ::
        $python3 foldersync
