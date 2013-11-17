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

import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtGui, QtCore

from P4 import P4, P4Exception

from .errors import log_warnings_and_errors, ErrorHandler


#def _load_user_details():
#    """
#    """
#    settings = QtCore.QSettings("Shotgun Software", "tk-framework-perforce")
#    
#    user_details = {}
#    
#    array_sz = settings.beginReadArray("user_connection_details")
#    for ai in range(0, array_sz):
#        settings.setArrayIndex(ai):
#        project_id = settings.value("project_id").toInt()
#        user = settings.value("user").toString()
#        client = settings.value("client").toString()
#        
#        user_details[project_id] = {"user":user, "client":client}
#        
#    settings.endArray()
#    
#    return user_details
#
#
#def _save_user_details(user_details):
#    """
#    """
#    settings = QtCore.QSettings("Shotgun Software", "tk-framework-perforce")
#    
#    settings.beginWriteArray("user_connection_details")
#    
#    for ai, (project_id, details) in enumerate(user_details.iteritems()):
#        settings.setArrayIndex(ai)
#        
#        settings.setValue("project_id", project_id)
#        settings.setValue("user", details.get("user", ""))
#        settings.setValue("client", details.get("client", ""))
#        
#    settings.endArray()
    

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
    p4.port = str(fw.get_setting("port"))

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

    
class ConnectionHandler(object):
    def __init__(self, fw):
        self._fw = fw
        self._p4 = None
        self._error_handler = ErrorHandler(fw)

    @property
    def connection(self):
        return self._p4

    def disconnect(self):
        """
        Disconnect the current p4 connection if there is one
        """
        if self._p4 and self._p4.connected():
            self._p4.disconnect()
        self._p4 = None

    def connect_to_server(self, host, port):
        """
        Open a connection to the server specified by host & port.
        Returns a new P4 connection object if successful 
        """
        # create new P4 instance 
        p4 = P4()
    
        # load the server configuration:
        p4.host = host
        p4.port = str(port)
    
        # attempt to connect to the server:
        host_port = ":".join([item for item in [p4.host, p4.port] if item])
        try:
            self._fw.log_debug("Attempting to connect to %s" % host_port)
            p4.connect()
        except P4Exception, e:
            self._error_handler.log(p4)
            #log_warnings_and_errors(self._fw, p4)
            raise TankError("Perforce: Failed to connect to %s - '%s'" % (host_port, (p4.errors or p4.warnings or [""])[0]))
        
        self._p4 = p4
        return self._p4

    def login_user(self, user):
        """
        Log-in the specified Perforce user if required.
        """
        if not self._p4 or not self._p4.connected():
            raise TankError("Perforce: Unable to log user in without an open Perforce connection!")
        
        # set the current p4 user:
        self._p4.user = str(user)
        
        login_req = self._login_required()
        if login_req:
            # prompt for password:
            # ...
            error_msg = None
            
            while True:
                pw = self.prompt_for_password(error_msg)
                if pw == None:
                    # User hit cancel!
                    raise TankError("Unable to login user %s without a password!" % user)

                try:
                    # attempt to log-in using this password
                    self._p4.password = pw
                    self._p4.run_login()
                except P4Exception:
                    self._error_handler.log(self._p4)
                    
                    # update the error message and try again:
                    error_msg = "Log-in failed: %s" % (self._p4.errors or self._p4.warnings or [""])[0]
                    continue
                else:
                    # successfully logged in!
                    break
        
    def prompt_for_password(self, error_msg, parent_widget=None):
        """
        Prompt the user to enter the password required by Perforce.
        
        :return: String - the password the user entered or None if they
                 cancelled entry
        """
        try:
            
            # show the password entry dialog:
            p4_widgets = self._fw.import_module("widgets")
            res, widget = self._fw.engine.show_modal("Perforce Password", self._fw, p4_widgets.PasswordForm, False, error_msg, 
                                                     parent_widget)
            if res == QtGui.QDialog.Accepted:
                return widget.password
            
        except TankError, e:
            pass
        
        return None
    
    def prompt_for_workspace(self, user, initial_ws, parent_widget=None):
        """
        Prompt the user to enter/select the client/workspace to use
        
        :return: String - the workspace to use for the connection
        """
        if not self._p4 or not self._p4.connected():
            raise TankError("Unable to retrieve list of workspaces without an open Perforce connection!")
        
        try:
            # get all avaliable workspaces for the current user and this host:
            import socket
            host = socket.gethostname()
            
            all_workspaces = self._p4.run_clients("-u", user)
            filtered_workspaces = [ws for ws in all_workspaces if ws.get("Host") == host]
            
            # show the password entry dialog:
            p4_widgets = self._fw.import_module("widgets")
            res, widget = self._fw.engine.show_modal("Perforce Workspace", self._fw, p4_widgets.SelectWorkspaceForm, 
                                                     self._p4.host, int(self._p4.port), user,
                                                     filtered_workspaces, initial_ws, parent_widget)
            if res == QtGui.QDialog.Accepted:
                return widget.workspace_name
            
        except TankError, e:
            pass
        
        return None
    
    def connect(self):
        """
        Utility method that returns a connection using the current configuration.  If a connection
        can't be established and the user is in ui mode then they will be prompted to edit the
        connection details.
        """
        host = self._fw.get_setting("host")
        port = self._fw.get_setting("port")
        user = self._fw.execute_hook("hook_get_perforce_user", sg_user = sgtk.util.get_current_user(self._fw.sgtk))
        workspace = self._get_last_workspace()
    
    def _get_last_workspace(self):
        """
        """
        return "ad_zombie_racer"
    
    def _save_last_workspace(self):
        """
        """
        pass  
        
    def connect_with_dlg(self):
        """
        """
        host = self._fw.get_setting("host")
        port = self._fw.get_setting("port")
        user = self._fw.execute_hook("hook_get_perforce_user", sg_user = sgtk.util.get_current_user(self._fw.sgtk))
        
        # first, attempt to connect to the server:port:
        try:
            self.connect_to_server(host, port)
        except TankError, e:
            QtGui.QMessageBox.information(None, "Failed to connect to Perforce server!", "%s" % e)
            return
        
        try:
            
            p4_widgets = self._fw.import_module("widgets")
        
            # get initial user & workspace from settings:    
            initial_workspace = ""
            
            # show the connection dialog:
            result, _ = self._fw.engine.show_modal("Perforce Connection", self._fw, p4_widgets.OpenConnectionForm, host, 
                                                   port, user, initial_workspace, self._setup_connection_dlg)
           
            if result == QtGui.QDialog.Accepted:
                # all good so return the p4 object:
                return self._p4

        except:
            self._fw.log_exception("Failed to Open Connection dialog!")
    
    def _setup_connection_dlg(self, widget):
        """
        """
        widget.browse_workspace_clicked.connect(self._on_browse_workspace)
        widget.open_clicked.connect(self._on_open_connection)
    
    def _on_browse_workspace(self, widget):
        """
        """
        if not widget.user:
            return

        # make sure the current user is logged in:        
        try:
            self.login_user(widget.user)
        except TankError, e:
            # likely that the user isn't valid!
            QtGui.QMessageBox.information(widget, "Failed to log-in!", "%s" % e)
            return
        
        # prompt user to select workspace:
        ws_name = self.prompt_for_workspace(self._p4.user, widget.workspace, widget)
        if ws_name:
            widget.workspace = ws_name
        
    def _on_open_connection(self, widget):
        """
        """
        if not widget.user or not widget.workspace:
            return
        
        # make sure the current user is logged in:        
        try:
            self.login_user(widget.user)
        except TankError, e:
            # likely that the user isn't valid!
            QtGui.QMessageBox.information(widget, "Failed to log-in!", "%s" % e)
            return
        
        # make sure the workspace is valid:
        try:
            self._validate_workspace(widget.user, widget.workspace)        
        except TankError, e:
            QtGui.QMessageBox.information(widget, "Invalid Workspace!", "%s" % e)
            return
        
        # success so lets close the widget!
        widget.close()

    def _validate_workspace(self, user, workspace):
        """
        """
        try:
            workspaces = self._p4.run_clients("-e", str(workspace))
        except P4Exception:
            raise TankError("Perforce: %s" % (self._p4.errors or self._p4.warnings or [""])[0])

        if not workspaces:
            raise TankError("Workspace '%s' does not exist!" % (workspace))

        ws_users = [ws.get("Owner") for ws in workspaces]
        if user not in ws_users:
            raise TankError("Workspace '%s' is not owned by user '%s'" % (workspace, user))

    def _login_required(self, min_timeout=300):
        """
        Determine if the specified user is required to log in.
        """
        # first, check to see if the user is required to log in:
        users = []
        try:
            # This will raise a P4Exception if the user isn't valid:
            users = self._p4.run_users(self._p4.user)
        except P4Exception:
            self._error_handler.log(self._p4)
            #log_warnings_and_errors(fw, p4)
            raise TankError("Perforce: Failed to query user info from server for user '%s' - '%s'" 
                                % (self._p4.user, (self._p4.errors or self._p4.warnings or [""])[0]))
    
        # users = [...{'Password': 'enabled'}...]
        if not users[0].get("Password") == "enabled":
            return False
        
        # get the list of tickets for the current user
        try:
            p4_res = self._p4.run_login("-s")
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
    
def connect_with_dlg(fw):
    """
    """
    
    handler = ConnectionHandler(fw)
    return handler.connect_with_dlg()
    
    
    



    