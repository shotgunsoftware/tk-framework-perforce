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
from datetime import datetime

import sgtk
from sgtk import Hook, TankError
from tank_vendor.shotgun_api3 import sg_timezone

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

class FilterWorkFiles(Hook):
    """
    Hook that can be used to filter the list of work files found by the app for the current
    Work area
    """
    
    def execute(self, work_files, **kwargs):
        """
        Main hook entry point
        
        :param work_files:   List of dictionaries 
                             A list of  dictionaries for the current work area within the app.  Each
                             item in the list is a Dictionary of the form:
                             
                             {
                                 "work_file" : {
                                 
                                     Dictionary containing information about a single work file.  Valid entries in
                                     this dicitionary are listed below but may not be populated when the hook is
                                     executed!
                                     
                                     It is intended that custom versions of this hook should populate these fields
                                     if needed before returning the filtered list  
                                 
                                     version_number    - version of the work file
                                     name              - name of the work file
                                     task              - task the work file should be associated with
                                     description       - description of the work file
                                     thumbnail         - thumbnail that should be used for the work file
                                     modified_at       - date & time the work file was last modified
                                     modified_by       - Shotgun user entity dictionary for the person who
                                                         last modified the work file
                                 }
                             }
                             
                                                         
        :return List:        The filtered list of dictionaries of the same form as the input 'work_files' 
                             list
        """
        app = self.parent

        # open a perforce connection:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        
        p4 = p4_fw.connection.connect()
        if not p4:
            raise TankError("Failed to connect to Perforce!")

        # find unique list of paths for this list of work files:
        local_paths = set()
        file_path_pairs = []
        for entry in work_files:
            work_file = entry.get("work_file")
            if not work_file:
                continue
            
            local_path = work_file.get("path")
            if not local_path:
                continue
            
            local_paths.add(local_path)
            file_path_pairs.append((entry, local_path))
           
        # find perforce details for these files: 
        p4_file_details = p4_fw.util.get_client_file_details(p4, list(local_paths))
        
        # find the details about the specific revision of each file returned - this is
        # so that we have the modified by information.
        path_revision_to_path = {}
        for path, details in p4_file_details.iteritems():
            if not details:
                continue
            
            have_rev = details.get("haveRev")
            head_rev = details.get("headRev")
            if not have_rev or not head_rev or have_rev == head_rev:
                continue
            
            path_revision_to_path["%s#%s" % (path, have_rev)] = path

        if path_revision_to_path:
            p4_file_revision_details = p4_fw.util.get_client_file_details(p4, path_revision_to_path.keys())
            
            # update any file details to use the revision specific details:
            for path_revision, details in p4_file_revision_details.iteritems():
                if not details:
                    continue
                path = path_revision_to_path.get(path_revision)
                p4_file_details[path] = details

        # finally, grab the change details for all changes referenced by these files - this
        # is so that we have the user and description info.
        changes = set()
        for path, details in p4_file_details.iteritems():
            if not details:
                continue

            have_rev = details.get("haveRev")
            head_rev = details.get("headRev")
            if not have_rev or not head_rev or have_rev != head_rev:
                # can't reliably get the change!
                continue
            
            change = details.get("headChange")
            if change:
                changes.add(change)
        p4_change_details = p4_fw.util.get_change_details(p4, list(changes)) if changes else {}

        # find additional info for files that are in depot:
        filtered_work_files = []
        for entry, local_path in file_path_pairs:
            work_file = entry.get("work_file")
            
            p4_details = p4_file_details.get(local_path)
            if p4_details:
                # add in extra info from file details:
                if "haveRev" in p4_details:
                    have_rev = int(p4_details["haveRev"])
                    work_file["version_number"] = have_rev
                    
                    if "headModTime" in p4_details and int(p4_details.get("headRev", "0")) == have_rev:
                        head_mod_time = p4_details["headModTime"]
                        work_file["modified_at"] = datetime.fromtimestamp(int(head_mod_time), tz=sg_timezone.local) 

                # add in information from change:
                change = p4_details.get("headChange")
                change_details = p4_change_details.get(change) if change else None
                if change_details:
                    if "desc" in change_details:
                        work_file["description"] = change_details["desc"]
                    if "user" in change_details:
                        work_file["modified_by"] = p4_fw.get_shotgun_user(change_details["user"])
                        
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
            
            filtered_work_files.append(entry)
        
        return filtered_work_files
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            