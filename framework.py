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
            self.log_debug("P4Python successfully loaded!")
            return
        
        # add the python version, p4d version, & platform specific path to sys.path:
        py_version_str = "%d%d" % (sys.version_info[0], sys.version_info[1])
        p4d_version_str = "2012.1" # (AD) - should this be driven from the config?
        os_str = {"darwin":"mac", "win32":"win64" if sys.maxsize > 2**32 else "win32", "linux2":"linux"}[sys.platform]
        p4python_dir = "p4python_py%s_p4%s_%s" % (py_version_str, p4d_version_str, os_str)
        p4_path = os.path.join(self.disk_location, "resources", p4python_dir, "python")
        if os.path.exists(p4_path):
            sys.path.append(p4_path)
            
        # finally, check that it's working!
        try:
            from P4 import P4
        except:
            self.log_error("Failed to load P4Python!")
        else:
            self.log_debug("P4Python successfully loaded!")
            
            
            
            
  