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

from sgtk import TankError

import re

DEFAULT_FSTAT_FIELDS = ["clientFile", "depotFile", "haveRev", "headRev"]

def client_to_depot_paths(p4, client_paths):
    """
    Utility method to return a list of depot paths given a list of client/local
    paths.  An empty string is returned for any local paths that don't map to a 
    depot path using the specified p4 connection.
    
    :param p4:            An open Perforce connection
    :param client_paths:  List of local/client paths to find depot paths for  
    """
    if isinstance(client_paths, basestring):
        client_paths = [client_paths]
    
    client_file_details = get_client_file_details(p4, client_paths)
    depot_paths = []
    for client_path in client_paths:
        depot_path = client_file_details.get(client_path, {}).get("depotFile", "")
        depot_paths.append(depot_path)
    return depot_paths    

def depot_to_client_paths(p4, depot_paths):
    """
    Utility method to return a list of client/local paths given a list of depot
    paths.  An empty string is returned for any depot paths that don't map to the 
    local client using the specified p4 connection.
    
    :param p4:            An open Perforce connection
    :param depot_paths:   List of depot paths to find client/local paths for  
    """
    if isinstance(depot_paths, basestring):
        depot_paths = [depot_paths]
            
    depot_file_details = get_depot_file_details(p4, depot_paths)
    client_paths = []
    for depot_path in depot_paths:
        client_path = depot_file_details.get(depot_path, {}).get("clientFile", "")
        client_paths.append(client_path)
    return client_paths

def get_client_file_details(p4, paths, fields = DEFAULT_FSTAT_FIELDS, flags = []):
    """
    Return file details for the specified list of local/client paths as 
    a dictionary keyed by the local/client path.
    
    :param p4:        An open Perforce connection
    :param paths:     List of local/client paths to find details for
    :param fields:    List of Perforce fstat fields to return
    :param flags:     List of additional flags to pass to fstat
    """
    if isinstance(paths, basestring):
        paths = [paths]    
    return __run_fstat(p4, paths, ["clientFile", "headRev"] + fields, flags, "clientFile")
    
def get_depot_file_details(p4, paths, fields = DEFAULT_FSTAT_FIELDS, flags = []):
    """
    Return file details for the specified list of depot paths as 
    a dictionary keyed by the depot path.
    
    :param p4:        An open Perforce connection
    :param paths:     List of depot paths to find details for
    :param fields:    List of Perforce fstat fields to return
    :param flags:     List of additional flags to pass to fstat
    """
    if isinstance(paths, basestring):
        paths = [paths]    
    return __run_fstat(p4, paths, ["depotFile", "headRev"] + fields, flags, "depotFile")

def check_out_file(p4, path, add_if_not_exists=False):
    """
    Check out the specified path for edit.
    
    :param p4:                    An open Perforce connection
    :param path:                  Path to check out
    :param add_if_not_exists:     If True then add the file to the depot if possible
    """
    
    # first get the current status of the file:
    file_stat = []
    try:
        file_stat = p4.run_fstat(path)
    except P4Exception, e:
        raise TankError("Perforce: Failed to run fstat on file - %s" % (p4.errors[0] if p4.errors else e))        
    
    if not file_stat:
        if add_if_not_exists:
            # file is not in depot so lets try adding it:
            try:
                # add the file to the depot:
                file_stat = p4.run_add(path)
            except P4Exception, e:
                raise TankError("Perforce: Failed to add file - %s" % (p4.errors[0] if p4.errors else e))
    else:
        if "action" not in file_stat or file_stat["action"] != "edit":
            # (AD) - TODO - check if file is latest! - what about other actions (delete, etc.)
            try:
                p4.run_edit(path)
            except P4Exception, e:
                raise TankError("Perforce: Failed to checkout file - %s" % (p4.errors[0] if p4.errors else e))

    if not file_stat:
        raise TankError("Perforce: File '%s' does not exist in depot!" % path)


def __run_fstat(p4, file_paths, fields, flags, type):
    """
    Return file details for the specified list of paths by calling
    fstat on them.
    
    :param p4:            An open Perforce connection
    :param file_paths:    Paths of files to run fstat on 
    :param fields:        Perforce fields to query
    :param flags:         Additional flags to pass to fstat
    :param type:          Path type to key result by - either 'depotFile' or 'clientFile'
    
    :return dict:         Dictionary of the results for each file keyed by type.
    """
    if not file_paths:
        return {}
    
    # query files using fstat
    p4_res = []
    try:
        # set up list of flags to pass to fstat:
        flags = list(flags) if flags else []

        # special case handling for querying attributes as this requires
        # the -Oa flag to be passed
        if "-Oa" not in flags:
            for field in fields:
                if (field.startswith("attr-") or field.startswith("attrProp-")
                    or field.startswith("openattr-") or field.startswith("openattrProp-")):
                    flags.append("-Oa")
                    break
        
        # ensure any fields follow -T flag:
        if "-T" in flags:
            flags.remove("-T")
        if fields:
            fields_str = ",".join(fields)
            flags.append("-T")
            flags.append(fields_str)
            
        # run fstat:
        p4_res = p4.run_fstat(flags, file_paths)
    except P4Exception, e:
        # under normal circumstances, this shouldn't happen so just raise a TankError.
        raise TankError("Perforce: Failed to run fstat on file(s) - %s" % (p4.errors[0] if p4.errors else e))
    
    # match up results with files:
    # build a lookup with file_path & headrevision:
    p4_res_lookup = {}
    for item in p4_res:
        if type not in item or "headRev" not in item:
            continue
        
        head_rev = int(item["headRev"])
        path_key = item[type].replace("\\", "/")
        
        p4_res_lookup.setdefault(path_key, dict())[head_rev] = item
        
    # regex to split out path and revision from a Perforce path
    regex = re.compile("(?P<path>.+)#(?P<revision>[0-9]+)$")
    
    p4_file_details = {}
    for file_path in file_paths:
        # support file_path of forms:
        #   foo/bar.png
        #   foo/bar.png#version
        file_key = file_path.replace("\\", "/")
        file_rev = None
        
        # see if the paths is a path#version combination:
        mo = regex.match(file_key)
        if mo:
            file_key = mo.group("path").strip()
            file_rev = int(mo.group("revision").strip())

        # find the file details for this path:
        file_details = {}
        p4_results = p4_res_lookup.get(file_key, {})
        if p4_results:
            if file_rev is not None:
                file_details = p4_results.get(file_rev, {})
            elif len(p4_results) == 1:
                file_details = p4_results.values()[0]

        p4_file_details[file_path] = file_details
        
    return p4_file_details



