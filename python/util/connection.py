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
Common Perforce connection utility methods
"""

import os

from sgtk import TankError
from P4 import P4, P4Exception

from .errors import log_warnings_and_errors

def _load_user_config():
    """
    (AD) - TEMP
    """
    config = {"user":"Alan", "client":"ad_zombie_racer"}
    
    # load in any missing pieces from environment if they've
    # been defined
    os_lookup = {"user":"P4USER", "client":"P4CLIENT"}
    for key, env_var in os_lookup.iteritems():
        if key not in config:
            env_val = os.environ.get(env_var)
            if env_val:
                config[key] = env_val
    
    return config

def _login_required(p4, fw, min_timeout=300):
    """
    Determine if login is required for the current user
    """
    # first, check to see if the user is required to log in:
    users = []
    try:
        # This will raise a P4Exception if the user isn't valid:
        users = p4.run_users(p4.user)
    except P4Exception:
        log_warnings_and_errors(fw, p4)
        raise TankError("Perforce: Failed to query user info from server for user '%s' - '%s'" 
                            % (p4.user, (p4.errors or p4.warnings or [""])[0]))

    # users = [...{'Password': 'enabled'}...]
    if not users[0].get("Password") == "enabled":
        return False
    
    # get the list of tickets for the current user
    try:
        p4_res = p4.run_login("-s")
        if not p4_res:
            # no ticket so login required
            return True
    except P4Exception:
        # exception raised because user isn't logged in!
        # (AD) - are there other exceptions that could be raised?
        return True
        
    # p4_res is of the form:
    # [{'TicketExpiration': '43026', 'User': 'Alan'}]        
    for ticket_status in p4_res:
        timeout = 0
        try:
            timeout = int(ticket_status.get("TicketExpiration", "0"))
        except ValueError:
            timeout=0
        if timeout >= min_timeout:
            # user is logged in and has enough 
            # time remaining
            return False

    # user isn't logged in!
    return True

def connect(fw):
    """
    Open a connection using the configured settings, prompting
    the user if required. 
    """
    
    # create new P4 instance 
    p4 = P4()

    # load the server configuration:
    p4.host = fw.get_setting("host")
    p4.port = fw.get_setting("port")

    # attempt to connect to the server:
    host_port = ":".join([item for item in [p4.host, p4.port] if item])
    try:
        fw.log_debug("Attempting to connect to %s" % host_port)
        p4.connect()
    except P4Exception, e:
        log_warnings_and_errors(fw, p4)
        raise TankError("Perforce: Failed to connect to %s - '%s'" % (host_port, (p4.errors or p4.warnings or [""])[0]))
        
    # next, get the user config:
    user_config = _load_user_config()
    p4.user = user_config.get("user", "")
    
    # See if the user needs to log-in:
    login_req = _login_required(p4, fw)
    if login_req:
        fw.log_debug("Logging in user '%s'" % p4.user)
        p4.password = "spiders"
        try:
            p4.run_login()
        except P4Exception:
            log_warnings_and_errors(fw, p4)
            raise TankError("Perforce: Failed to login user %s - '%s'" % (p4.user, (p4.errors or p4.warnings or [""])[0]))    
            
    # Finally, get the client:
    p4.client = user_config.get("client", "")

    # and validate:    
    clients = []
    try:
        clients = p4.run_clients("-u", p4.user)
    except P4Exception:
        log_warnings_and_errors(fw, p4)
        raise TankError("Perforce: Failed to query clients for user %s - '%s'" % (p4.user, (p4.errors or p4.warnings or [""])[0]))
    
    client_names = [client["client"] for client in clients]
    if p4.client not in client_names:
        raise TankError("Perforce: Client '%s' does not exist for user '%s'" % (p4.client, p4.user))
    
    # all good!    
    return p4
    