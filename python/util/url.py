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

import re
import urlparse

import sgtk

URL_REVISION_PARAM_REGEX = re.compile("^rev=(?P<revision>[0-9]+)$")

# ensure that parsing Perforce url's seperates out the netloc and params
PERFORCE_SCHEME = "perforce"
if PERFORCE_SCHEME not in urlparse.uses_netloc:
    urlparse.uses_netloc.append(PERFORCE_SCHEME)
    urlparse.uses_params.append(PERFORCE_SCHEME)
    
def url_from_depot_path(depot_path, revision=None):
    """
    Construct a uniform perforce url for the specified
    depot path.  The depot path will already be quoted
    correctly.  
    
    The url will be of the form:
    
        perforce://server:port/depot/path/to/the/file;rev=#
    
    :param depot_path:    The depot path to construct a url for
    :returns:             url representing the specified depot path
    """
    fw = sgtk.platform.current_bundle()
    
    # remove double slashes at start of path:
    url_path = "/%s" % depot_path.lstrip("/")
    
    # if revision is specified then append it to the path:
    params = ""
    if revision != None:
        params = "rev=%d" % revision
    
    # add server & port (always use 'server' for this rather than an alias)
    netloc = fw.get_setting("server")
    if netloc.isdigit():
        # assume p4.port is port on localhost:
        netloc = "localhost:%s" % netloc
    
    # construct url:
    return urlparse.urlunparse((PERFORCE_SCHEME, netloc, url_path, params, "", ""))

def depot_path_from_url(url, validate_server=True):
    """
    Extract the depot path from a perforce url of the form:
    
        perforce://server:port/depot/path/to/the/file
    
    :param url:                The url to extract the path from
    :param validate_server:    If True then validate that the server matches
                               the current Perforce connection 
    """
    fw = sgtk.platform.current_bundle()
    
    res = urlparse.urlparse(url)
    if res.scheme != PERFORCE_SCHEME:
        return
    
    if validate_server:
        if not res.netloc:
            # no server specified in the url!
            return
        
        # check that netloc is server or one of the aliases if set.  The
        # aliases are intended to allow old publish data to be used in
        # the event that the server is moved/renamed.
        server_is_valid = False
        for server in [fw.get_setting("server")] + fw.get_setting("server_aliases"): 
            if res.netloc == server:
                server_is_valid = True
                break
            elif server.isdigit():
                # special case handling when only the server port has been entered:
                if res.netloc == ("localhost:%s" % server):
                    server_is_valid = True
                    break
             
        if not server_is_valid:
            return

    # depot path should always start with '//':
    depot_path = "//%s" % res.path.lstrip("/")

    # check to see if a revision is specified in the params:
    revision = None
    if res.params:
        for param in res.params.split("&"):
            mo = URL_REVISION_PARAM_REGEX.match(param)
            if mo:
                revision = mo.group("revision")

    # return valid depot path:    
    return (depot_path, revision)