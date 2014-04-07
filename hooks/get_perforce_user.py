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
Hook that gets called to return the current Perforce user for a
specified Shotgun user
"""

import sgtk
import os, sys
 
class GetPerforceUser(sgtk.Hook):
    
    def execute(self, sg_user, **kwargs):
        """
        Return the Perforce username associated with the specified shotgun user
        
        :param sg_user:  Dictionary
                         The shotgun user entity fields
                     
        :returns:        String
                         The Perforce username for the specified Shotgun user
        """
        
        if not sg_user:
            # can't determine Perforce user if we don't know sg user!
            return None
        
        # default implementation just uses the users login:
        if "login" in sg_user:
            return sg_user["login"]
        
        sg_res = self.parent.shotgun.find_one("HumanUser", [["id", "is", sg_user["id"]]], ["login"])
        if sg_res:
            return sg_res.get("login")
        
        
        