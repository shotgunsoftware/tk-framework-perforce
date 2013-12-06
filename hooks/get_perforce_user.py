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
        
        :sg_user:    Dictionary
                     The shotgun user entity fields
                     
        :returns:    String
                     The Perforce username for the specified Shotgun user
        """
        
        if not sg_user:
            # can't determine Perforce user if we don't know sg user!
            return None
        
        if not "id" in sg_user:
            # very bad!
            raise sgtk.TankError("'id' field missing from Shotgun user dictionary!")

        # default implementation looks for the 'sg_perforce_user' field on the HumanUser entity.  If
        # that fails then it falls back to the login field        
        sg_res = self.parent.shotgun.find_one("HumanUser", [["id", "is", sg_user["id"]]], ["sg_perforce_user", "login"])
        if sg_res:
            return sg_res.get("sg_perforce_user") or sg_res.get("login")
            
        return None
        
        
        