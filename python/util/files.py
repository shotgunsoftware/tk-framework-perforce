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
Common utilities for working with Perforce files
"""

import os

from P4 import P4Exception

DEFAULT_FSTAT_FIELDS = "clientFile,depotFile,haveRev,headRev"

def get_client_file_details(p4, paths, fields = DEFAULT_FSTAT_FIELDS):
    """
    Return file details for the specified list of local/client paths
    """
    return _run_fstat(p4, paths, ",".join(["clientFile", DEFAULT_FSTAT_FIELDS]), "clientFile")
    
def get_depot_file_details(p4, paths, fields = DEFAULT_FSTAT_FIELDS):
    """
    Return file details for the specified list of depot paths
    """
    return _run_fstat(p4, paths, ",".join(["depotFile", DEFAULT_FSTAT_FIELDS]), "depotFile")

def _run_fstat(p4, file_paths, fields, type):
    """
    Return file details for the specified list of paths
    """
    p4_res = []
    try:
        p4_res = p4.run_fstat("-T", fields, file_paths)
    except P4Exception:
        pass
    
    # match up files with p4_files:
    p4_res_lookup = {}
    for item in p4_res:
        if type not in item:
            continue
        key = item[type].replace("\\", "/")
        p4_res_lookup[key] = item
        
    p4_file_details = {}
    for file_path in file_paths:
        key = file_path.replace("\\", "/")
        p4_file_details[file_path] = p4_res_lookup.get(key, {})
        
    return p4_file_details