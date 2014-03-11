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
import re
import urllib
import urlparse

from P4 import P4Exception, Map as P4Map # Prefix P4 for consistency

import sgtk
from sgtk import TankError

from .url import depot_path_from_url

# regex to split out path and revision from a Perforce path
PATH_REVISION_REGEX = re.compile("(?P<path>.+)#(?P<revision>[0-9]+)$")
PATH_CHANGE_REGEX = re.compile("(?P<path>.+)@(?P<change>[0-9]+)$")

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
        
    # check that all client paths are actually under the current workspace root
    # otherwise fstat will raise an exception:
    client_root = __get_client_root(p4)
    # (TODO) - this might need to be a little more robust!
    valid_client_paths = [path for path in client_paths if path.startswith(client_root)]

    client_file_details = get_client_file_details(p4, valid_client_paths)
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
            
    # filter list of depot paths that are mapped in the current client:
    map = __get_client_view(p4)
    mapped_depot_paths = [path for path in depot_paths if map.includes(path)]
            
    depot_file_details = get_depot_file_details(p4, mapped_depot_paths)
    client_paths = []
    for depot_path in depot_paths:
        client_path = depot_file_details.get(depot_path, {}).get("clientFile", "")
        client_paths.append(client_path)
    return client_paths

def get_client_file_details(p4, paths, fields = [], flags = []):
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
        
    # (AD) - does this also need to filter input list?
        
    return __run_fstat_and_aggregate(p4, paths, fields, flags, "clientFile")
    
def get_depot_file_details(p4, paths, fields = [], flags = []):
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
    
    # (AD) - does this also need to filter input list?  What if there is no client?
    
    return __run_fstat_and_aggregate(p4, paths, fields, flags, "depotFile")

def sync_published_file(p4, published_file_entity, latest=True):#, dependencies=True):
    """
    Sync the specified published file to the current workspace.
    """
    # depot path is stored in the path as a url:
    p4_url = published_file_entity.get("path", {}).get("url")
        
    # convert from perforce url, validating server:
    path_and_revision = depot_path_from_url(p4_url)
    depot_path = path_and_revision[0] if path_and_revision else None
    if not depot_path:
        # either an invalid path or different server so skip
        raise TankError("Failed to find Perforce file revision for %s" % p4_url)

    revision = None
    if not latest:
        revision = published_file_entity.get("version_number")

    sync_args = []
    sync_path = depot_path
    if revision:
        sync_path = "%s#%d" % (depot_path, revision)
    
    # sync file:
    try:        
        p4.run_sync(sync_args, sync_path)
    except P4Exception, e:
        raise TankError("Perforce: Failed to sync file %s - %s" % (sync_path, p4.errors[0] if p4.errors else e))
    
    # (TODO) handle dependencies
    # ...

def open_file_for_edit(p4, path, add_if_new=True, test_only=False):
    """
    Helper method to open the specified file for editing, optionally adding the file to 
    the depot as well.
    
    :param p4:            An open Perforce connection
    :param path:          The path to check-out/add
    :param add_if_new:    If True and the file isn't currently in Perforce then it will
                          be added
    :param test_only:     Test that the file can be checked-out/added but don't actually
                          perform the action
    """
    # get the current status of the file:
    file_stat = []
    try:
        file_stat = p4.run_fstat(path)
    except P4Exception, e:
        raise TankError("Failed to run p4 fstat on file - %s" % (p4.errors[0] if p4.errors else e))
    
    if file_stat:
        if not isinstance(file_stat, list) or len(file_stat) != 1 or not isinstance(file_stat[0], dict):
            raise TankError("p4 fstat returned unexpected result for file '%s'!" % path)
        file_stat = file_stat[0]
        
        # file is in Perforce so ensure that it can be checked out:
        # - basically, it's not opened by any other users
        num_other_opened = int(file_stat.get("otherOpens", "0"))
        if num_other_opened > 0:
            # raise error with the first other user that has the file open:
            open_by = file_stat.get("otherOpen", ["<unknown>"])[0]
            other_p4_user = open_by.split("@")[0]
            
            fw = sgtk.platform.current_bundle()
            other_sg_user = fw.get_shotgun_user(other_p4_user)
            if other_sg_user:
                other_sg_user = other_sg_user.get("name")
            if not other_sg_user:
                other_sg_user = other_p4_user
            raise TankError("File '%s' is already opened for '%s' by '%s'" 
                            % (path, file_stat.get("otherAction", ["<unknown>"])[0], other_sg_user))
        
        if "action" in file_stat:
            # ok, so assume that we can edit the file - we won't
            # get latest though...
            if test_only:
                return
        else:
            if test_only:
                return
            
            # get latest if need to:
            head_rev = int(file_stat["headRev"])
            have_rev = int(file_stat.get("haveRev", "0"))
            
            if have_rev < head_rev:
                try:        
                    p4.run_sync(path)
                except P4Exception, e:
                    raise TankError("Failed to sync file '%s' to latest revision - %s" 
                                    % (path, p4.errors[0] if p4.errors else e))

        # and finally, check out the file to edit:
        try:
            p4.run_edit(path)
        except P4Exception, e:
            raise TankError("Failed to checkout file '%s' - %s" 
                            % (path, p4.errors[0] if p4.errors else e))
        
    elif add_if_new:
        # file isn't in Perforce yet:
        if test_only:
            # ensure file exists under the client root:
            try:
                p4.run_where(path)
            except P4Exception, e:
                raise TankError("Unable to add file '%s' to depot - %s"
                                % (path, p4.errors[0] if p4.errors else e))
        else:
            if not os.path.exists(path):
                raise TankError("Unable to add file '%s' to Perforce as it doesn't exist!" % path)
            
            # add file to depot:
            try:
                p4.run_add(path)
            except P4Exception, e:
                raise TankError("Failed to add file '%s' to depot - %s" 
                                % (path, p4.errors[0] if p4.errors else e))                    
        
def __get_client_root(p4):
    """
    Get the local root directory for the current workspace (as set
    in the p4 instance)
    
    :param p4:    The Perforce connection to use
    :returns:     The workspace root directory if found
    """
    try:
        client_spec = p4.fetch_client(p4.client)
        return client_spec._root.rstrip("\\/") + os.path.sep
    except P4Exception, e:
        raise TankError("Perforce: Failed to query the workspace root for user '%s', workspace '%s': %s" 
                        % (p4.user, p4.client, p4.errors[0] if p4.errors else e))
        
def __get_client_view(p4):
    """
    Get the view/mapping for the current workspace and user (as set
    in the p4 instance)
    
    :param p4:    The Perforce connection to use
    :returns:     The workspace root directory if found
    """
    try:
        client_spec = p4.fetch_client(p4.client)
        return P4Map(client_spec._view)
    except P4Exception, e:
        raise TankError("Perforce: Failed to query the workspace view/mapping for user '%s', workspace '%s': %s" 
                        % (p4.user, p4.client, p4.errors[0] if p4.errors else e))      

def __run_fstat_and_aggregate(p4, file_paths, fields, flags, type, ignore_deleted=True):
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
    
    if fields:
        # ensure type headRev and headAction are included in
        # the fields so we can extrapolate the results
        fields = list(fields)
        for required_field in [type, "headRev", "headAction"]:
            if not required_field in fields:
                fields.append(required_field)

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
        
    if ignore_deleted:
        # use filter to only return new additions/files:
        flags.append("-F")
        flags.append("^headAction=delete ^headAction=move/delete ^headAction=purge ^headAction=archive")
    
    # query files using fstat
    p4_res = []
    try:
        p4_res = p4.run_fstat(flags, file_paths)
    except P4Exception, e:
        # under normal circumstances, this shouldn't happen so just raise a TankError.
        raise TankError("Perforce: Failed to run fstat on file(s) - %s" % (p4.errors[0] if p4.errors else e))
    
    # match up results with files:
    # build a lookup with file_path & headRev
    # headRev is the revision of the result returned, haveRev is the revision
    # currently synced.  All returned results should have a headRev unless the
    # file has never been added to the depot
    p4_res_lookup = {}
    for item in p4_res:
        if type not in item:
            continue
        
        head_revision = int(item.get("headRev", "0"))
        path_key = item[type].replace("\\", "/")
        
        p4_res_lookup.setdefault(path_key, dict())[head_revision] = item
                
    p4_file_details = {}
    for file_path in file_paths:
        # support file_path of forms:
        #   foo/bar.png
        #   foo/bar.png#version
        #   foo/bar.png@change
        file_key = file_path.replace("\\", "/")
        file_rev = None
        file_change = None
        
        # see if the path is a path#version combination:
        mo = PATH_REVISION_REGEX.match(file_key)
        if mo:
            file_key = mo.group("path").strip()
            file_rev = int(mo.group("revision").strip())
        else:
            # see if the path is a path@change combination:
            mo = PATH_CHANGE_REGEX.match(file_key)
            if mo:
                file_key = mo.group("path").strip()
                file_change = int(mo.group("change").strip())

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



