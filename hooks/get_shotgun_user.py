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
Hook that gets called to return the Shotgun user for a specified Perforce user
"""

import sgtk
import os, sys
 
class GetShotgunUser(sgtk.Hook):
    
    def execute(self, p4_user, **kwargs):
        """
        Return the Shotgun user dictionary for the specified Perforce user
        
        :p4_user:    String
                     The Perforce user name
                     
        :returns:    Dictionary
                     The Shotgun user dictionary for the specified Perforce user
        """
        
        if not p4_user:
            # can't determine Shotgun user if we don't know p4 user!
            return None
        
        # default implementation looks for the 'sg_perforce_user' field on the HumanUser entity...
        sg_res = self.parent.shotgun.find_one("HumanUser", [["sg_perforce_user", "is", p4_user]], ["login"])
        if not sg_res:
            # ... but if that fails then we try the login field instead:
            sg_res =self.parent.shotgun.find_one('HumanUser', [['login', 'is', p4_user]])
            
        return sg_res        
        
        