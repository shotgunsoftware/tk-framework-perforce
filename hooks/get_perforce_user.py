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
        
        # default implementation returns the login for the current Shotgun user
        if "login" not in sg_user:
            raise sgtk.TankError("'login' field missing from Shotgun user dictionary!") 
        #return sg_user["login"]
            
        # alternate method looks for the 'sg_perforce_user' field on the HumanUser entity:
        if not "id" in sg_user:
            raise sgtk.TankError("'id' field missing from Shotgun user dictionary!")
        sg_res = self.parent.shotgun.find_one("HumanUser", [["id", "is", sg_user["id"]]], ["sg_perforce_user"])
        return sg_res["sg_perforce_user"]
        
        
        