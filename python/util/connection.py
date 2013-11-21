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

from .errors import ErrorHandler
from .user_settings import UserSettings
    
class ConnectionHandler(object):
    def __init__(self, fw):
        self._fw = fw
        self._p4 = None
        self._error_handler = ErrorHandler(fw)

    @property
    def connection(self):
        """
        """
        return self._p4

    def disconnect(self):
        """
        Disconnect the current p4 connection if there is one
        """
        if self._p4 and self._p4.connected():
            self._p4.disconnect()
        self._p4 = None

    def connect_to_server(self, server):
        """
        Open a connection to the specified server.
        Returns a new P4 connection object if successful 
        """
        # create new P4 instance 
        p4 = P4()
    
        # load the server configuration:
        p4.port = server
    
        # attempt to connect to the server:
        try:
            self._fw.log_debug("Attempting to connect to %s" % server)
            p4.connect()
        except P4Exception, e:
            self._error_handler.log(p4)
            raise TankError("Perforce: Failed to connect to %s - '%s'" % (server, (p4.errors or p4.warnings or [""])[0]))
        
        self._p4 = p4
        return self._p4

    def login_user(self, user, parent_widget=None):
        """
        Log-in the specified Perforce user if required.
        """
        if not self._p4 or not self._p4.connected():
            raise TankError("Perforce: Unable to log user in without an open Perforce connection!")
        
        # check that user is valid:
        self._validate_user(user)
        self._p4.user = str(user)
        
        login_req = self._login_required()
        if login_req:
            if self._do_login(parent_widget) != True:
                raise TankError("Perforce: Unable to login user %s without a password!" % user)
    
    def _prompt_for_workspace(self, user, initial_ws, parent_widget=None):
        """
        Prompt the user to enter/select the client/workspace to use
        
        :return: String - the workspace to use for the connection
        """
        if not self._p4 or not self._p4.connected():
            raise TankError("Unable to retrieve list of workspaces without an open Perforce connection!")
        
        try:
            # get all avaliable workspaces for the current user and this host machine:
            import socket
            host = socket.gethostname()
            
            all_workspaces = self._p4.run_clients("-u", user)
            filtered_workspaces = [ws for ws in all_workspaces if ws.get("Host") == host]
            
            # show the password entry dialog:
            p4_widgets = self._fw.import_module("widgets")
            res, widget = self._fw.engine.show_modal("Perforce Workspace", self._fw, p4_widgets.SelectWorkspaceForm, 
                                                     self._p4.port, user,
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
        # ensure that the connect method is called from the main thread
        # as it may need to present UI to the user:
        return self._fw.engine.execute_in_main_thread(self._connect)
        
    def _connect(self):
        """
        """
        server = self._fw.get_setting("server")
        user = self._fw.execute_hook("hook_get_perforce_user", sg_user = sgtk.util.get_current_user(self._fw.sgtk))
        workspace = self._get_current_workspace()

        try:
            # first, attempt to connect to the server:
            self.connect_to_server(server)
            
            # validate user:
            self._validate_user(user)
            self._p4.user = user
            
            # if log-in is required then log-in:
            login_req = self._login_required()
            if login_req:
                res = self._do_login()
                p4_widgets = self._fw.import_module("widgets")
                if res == p4_widgets.PasswordForm.SHOW_DETAILS:
                    # switch to connection dialog
                    raise TankError()
                elif not res:
                    # user cancelled log-in!
                    return
            
            # finally, validate the workspace:
            self._validate_workspace(workspace, user)
            self._p4.client = str(workspace)
            
            return self._p4
            
        except TankError, e:
            # failed to connect to server - switch to UI mode
            # if available instead:
            if self._fw.engine.has_ui:
                # just show the connection UI instead:
                return self.connect_with_dlg()
            else:
                # re-raise the last exception:
                raise

    def connect_with_dlg(self):
        """
        """
        server = self._fw.get_setting("server")
        user = self._fw.execute_hook("hook_get_perforce_user", sg_user = sgtk.util.get_current_user(self._fw.sgtk))
        
        # first, attempt to connect to the server:
        try:
            self.connect_to_server(server)
        except TankError, e:
            QtGui.QMessageBox.information(None, "Failed to connect to Perforce server!", "%s" % e)
            return
        
        try:
            
            p4_widgets = self._fw.import_module("widgets")
        
            # get initial user & workspace from settings:    
            initial_workspace = self._get_current_workspace()
            
            # show the connection dialog:
            result, _ = self._fw.engine.show_modal("Perforce Connection", self._fw, p4_widgets.OpenConnectionForm, 
                                                   server, user, initial_workspace, self._setup_connection_dlg)
           
            if result == QtGui.QDialog.Accepted:
                # all good so return the p4 object:
                self._save_current_workspace(self._p4.client)
                return self._p4

        except:
            self._fw.log_exception("Failed to Open Connection dialog!")

    def _do_login(self, parent_widget=None):
        """
        :return: Bool - True if the user successfully logged in, False otherwise 
        """
        error_msg = None
        password = None
        show_next_error = True
        
        # check to see if P4PASSWD is set
        env_val = os.environ.get("P4PASSWD")
        if env_val:
            password = env_val
            if password:
                show_next_error = False
            
        # loop until we successfully log in or cancel
        while True:
            if password:
                # attempt to log-in using this password
                try:
                    self._fw.log_debug("Attempting to log-in user %s" % self._p4.user)
                    self._p4.password = password
                    self._p4.run_login()
                except P4Exception:
                    self._error_handler.log(self._p4)

                    # update the error message and try again:
                    if show_next_error:
                        error_msg = "Log-in failed: %s" % (self._p4.errors or self._p4.warnings or [""])[0]
                    else:
                        show_next_error = True
                else:
                    # successfully logged in!
                    return True
            
            if self._fw.engine.has_ui:
            
                # show the password entry dialog:
                p4_widgets = self._fw.import_module("widgets")
                res, widget = self._fw.engine.show_modal("Perforce Password", self._fw, p4_widgets.PasswordForm,
                                                         self._p4.port, self._p4.user, 
                                                         (parent_widget == None), error_msg, parent_widget)
                
                if res == p4_widgets.PasswordForm.SHOW_DETAILS:
                    # just return the result:
                    return res
                elif res != QtGui.QDialog.Accepted:
                    # User hit cancel!
                    return False

                # keep track of password for next iteration:                
                password = widget.password
            
            else:
                # no UI so just raise error:
                raise TankError("Perforce: Unable to login user %s without a password!" % self._p4.user)
    
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
            self.login_user(widget.user, widget)
        except TankError, e:
            # likely that the user isn't valid!
            QtGui.QMessageBox.information(widget, "Failed to log-in!", "%s" % e)
            return
        
        # prompt user to select workspace:
        ws_name = self._prompt_for_workspace(self._p4.user, widget.workspace, widget)
        if ws_name:
            widget.workspace = ws_name
        
    def _on_open_connection(self, widget):
        """
        """
        if not widget.user or not widget.workspace:
            return
        
        # make sure the current user is logged in:        
        try:
            self.login_user(widget.user, widget)
        except TankError, e:
            # likely that the user isn't valid!
            QtGui.QMessageBox.information(widget, "Failed to log-in!", "%s" % e)
            return
        
        # make sure the workspace is valid:
        try:
            self._validate_workspace(widget.workspace, widget.user)
            self._p4.client = widget.workspace   
        except TankError, e:
            QtGui.QMessageBox.information(widget, "Invalid Workspace!", "%s" % e)
            return
        
        # success so lets close the widget!
        widget.close()
    
    def _get_current_workspace(self):
        """
        """
        workspace = ""
        if self._fw.context.project:
            settings = UserSettings("user_details")
            workspace = settings.get_client(self._fw.context.project["id"])
        
        if not workspace:
            # see if P4CLIENT is set in the environment:
            env_val = os.environ.get("P4CLIENT")
            if env_val:
                workspace = env_val
                
        return workspace
    
    def _save_current_workspace(self, workspace):
        """
        """
        if self._fw.context.project:
            settings = UserSettings("user_details")
            return settings.set_client(self._fw.context.project["id"], workspace) 

    def _validate_workspace(self, workspace, user):
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

    def _validate_user(self, user):
        """
        """
        # first, check to see if the user is required to log in:
        users = []
        try:
            users = self._p4.run_users()
        except P4Exception:
            self._error_handler.log(self._p4)
            raise TankError("Perforce: Failed to query users from server - '%s'" 
                                % ((self._p4.errors or self._p4.warnings or [""])[0]))
            
        user_names = [p4_user["User"] for p4_user in users]
        if not user in user_names:
            raise TankError("User '%s' is not a valid user")        

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
    
def connect(fw):
    """
    """
    handler = ConnectionHandler(fw)
    return handler.connect()
    



    