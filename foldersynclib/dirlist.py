#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 09:38:04 2017

@author: juliette
"""


def get_name(elt):
    return elt.name.lower()


class DirList:
    """List from scandir iterator."""
    def __init__(self, scandir_iterator):
        self.dirlist = sorted(scandir_iterator, key=get_name)
        self.namelist = [elt.name for elt in self.dirlist]

    def __iter__(self):
        return self.dirlist.__iter__()

    def __contains__(self, elt):
        return elt in self.namelist
