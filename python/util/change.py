# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Common utilities for working with Perforce changes
"""
from P4 import P4Exception

def create_change(p4, description):
    """
    Helper method to create a new change
    """
    
    # create a new changelist:
    new_change = None
    try:
        # fetch a new change, update the description, and save it:
        change_spec = p4.fetch_change()
        change_spec._description = str(description)
        # have to clear the file list as otherwise it would contain everything 
        # in the default changelist!
        change_spec._files = []
        p4_res = p4.save_change(change_spec)
    
        if p4_res:
            try:
                # p4_res should be like: ["Change 25 created."]
                new_change_id = int(p4_res[0].split()[1])
                new_change = str(new_change_id)
            except ValueError:
                raise TankError("Perforce: Failed to extract new change id from '%s'" % p4_res)
        
    except P4Exception, e:
        raise TankError("Perforce: %s" % (p4.errors[0] if p4.errors else e))
    
    if new_change == None:
        raise TankError("Perforce: Failed to create new change!")
    
    return new_change

def add_to_change(p4, change, file_paths):
    """
    Add the specified files to the specified change
    """
    try:
        # use reopen command which works with local file paths.
        # fetch/modify/save_change only works with depot paths!
        p4.run_reopen("-c", str(change), file_paths)
    except P4Exception, e:
        raise TankError("Perforce: %s" % (p4.errors[0] if p4.errors else e))
    
def find_change_containing(p4, path):
    """
    Find the current change that the specified path is in.
    """
    try:
        p4_res = p4.run_fstat(path)
    except P4Exception, e:
        raise TankError("Perforce: %s" % (p4.errors[0] if p4.errors else e))
    
    change = p4_res[0].get("change")
    return change

def submit_change(p4, change):
    """
    Submit the specified change
    """
    try:
        change_spec = p4.fetch_change("-o", str(change))
        p4.run_submit(change_spec)
    except P4Exception, e:
        raise TankError("Perforce: %s" % (p4.errors[0] if p4.errors else e))








