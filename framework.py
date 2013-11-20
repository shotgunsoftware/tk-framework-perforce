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
Framework for common Perforce functionality
"""

import tank
import platform
import sys
import traceback
import os

class PerforceFramework(tank.platform.Framework):

    ##########################################################################################
    # init and destroy
            
    def init_framework(self):
        self.log_debug("%s: Initializing..." % self)
        
        # initialize p4python:
        self.__init_p4python()
    
    def destroy_framework(self):
        self.log_debug("%s: Destroying..." % self)
    
    def connect(self):
        """
        """
        util = self.import_module("util")
        return util.connect(self)
        
    def connect_with_dlg(self):
        """
        """
        util = self.import_module("util")
        return util.connect_with_dlg(self)
        
    def __init_p4python(self):
        """
        Make sure that p4python is available and if it's
        not then add it to the path if we have a version
        we can use
        """
        try:
            from P4 import P4
        except:
            # ignore!
            pass
        else:
            # P4 already available!
            self.log_info("P4Python successfully loaded!")
            return
        
        # add the platform specific path to sys.path:
        # (AD) - this should be python version dependent as well!
        if sys.platform == "darwin":
            p4_path = os.path.join(self.disk_location, "resources","p4python_py26_p42012.1_mac", "python")
            sys.path.append(p4_path)
            
        self.log_info("")
            
        # finally, check that it's working!
        try:
            from P4 import P4
        except:
            self.log_error("Failed to load P4Python!")
        else:
            self.log_info("P4Python successfully loaded!")
            
            
            
            
  