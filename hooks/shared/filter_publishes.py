# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import sgtk
from sgtk import Hook, TankError

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

class FilterPublishes(Hook):
    """
    Hook that can be used to filter the list of publishes returned from Shotgun for the current
    location
    """
    def execute(self, publishes, **kwargs):
        """
        Main hook entry point
        
        :param publishes:    List of dictionaries 
                             A list of  dictionaries for the current location within the app.  Each
                             item in the list is a Dictionary of the form:
                             
                             {
                                 "sg_publish" : {Shotgun entity dictionary for a Published File entity}
                             }
                             
                                                         
        :return List:        The filtered list of dictionaries of the same form as the input 'publishes' 
                             list
        """
        app = self.parent

        # open a perforce connection:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        
        p4 = p4_fw.connection.connect()
        if not p4:
            raise TankError("Failed to connect to Perforce!")

        # find unique list of depot paths for this list of publishes:
        depot_paths = set()
        publish_path_pairs = []
        for publish in publishes:
            sg_publish = publish.get("sg_publish")
            if not sg_publish:
                continue
            
            sg_publish_path = sg_publish.get("path")
            if not sg_publish_path:
                continue
            
            depot_path_url = sg_publish_path.get("url")
            if not depot_path_url:
                continue
            
            # convert from perforce url, validating server:
            path_and_revision = p4_fw.util.depot_path_from_url(depot_path_url)
            depot_path = path_and_revision[0] if path_and_revision else None
            if not depot_path:
                # either an invalid path or different server so skip
                continue
            
            depot_paths.add(depot_path)
            publish_path_pairs.append((publish, depot_path))
            
        # find local paths for these depot paths (using the current client spec)
        p4_file_details = p4_fw.util.get_depot_file_details(p4, list(depot_paths))        
        
        # filter out any publishes that aren't mapped to the client or
        # that don't exist within the current project data root(s):
        project_data_roots = app.sgtk.roots
        
        filtered_publishes = []
        for entry, depot_path in publish_path_pairs:
            p4_details = p4_file_details.get(depot_path)
            if not p4_details:
                continue
            
            local_path = p4_details.get("clientFile")
            if not local_path:
                # file isn't mapped locally so skip
                continue
    
            # check that local path is understood by toolkit (check to find a 
            # matching template):
            template = app.sgtk.template_from_path(local_path)
            if not template:
                continue
            
            # update the local_path in the publish path dictionary:
            sg_publish = entry["sg_publish"]
            sg_publish["path"]["local_path"] = local_path
            
            # add editability information to the entry:
            editable = int(p4_details.get("otherOpens", "0")) == 0
            reason = None
            if not editable:
                other_actions = p4_details["otherAction"]
                other_open = p4_details["otherOpen"]
                
                user_actions = []
                for action, user_client in zip(other_actions, other_open):
                    
                    # separate user & client from user_client string:
                    at_pos = user_client.find("@")
                    user = user_client[:at_pos]
                    client = user_client[at_pos+1:] if at_pos else ""
                    
                    sg_user = p4_fw.get_shotgun_user(user)
                    if sg_user:
                        user = sg_user.get("name") or user
                    
                    user_actions.append(" %s by %s (in %s)" % (action.strip(), user, client or "unknown"))
                    
                reason = ("The file is currently open for%s" % ",".join(user_actions))
        
            entry["editable"] = {"can_edit":editable, "reason":reason}
            
            filtered_publishes.append(entry)            
    
        return filtered_publishes







