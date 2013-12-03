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

import sgtk
import platform
import sys
import os

class PerforceFramework(sgtk.platform.Framework):

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
        
        compiler_str = ""
        if sys.platform == "win32":
            # for windows, we may need to determine p4python based on compiler:
            compiler = platform.python_compiler()
            
            # default vc version for python 2.6 & 2.7 is 9 (VS2008):
            vc_version = 9
            
            # split the string - it will be something like this:
            # "MSC v.1500 64 bit (AMD64)"
            parts = compiler.split()
            if len(parts) > 2 and parts[0] == "MSC" and parts[1][:2] == "v.":
                # have a compatible string!
                try:
                    msc_version = int(parts[1][2:])
                    
                    # convert this to a vc version:
                    if msc_version >= 1800:
                        # follow convention of msc_version being 6 ahead of vc version!
                        vc_version = msc_version/100 - 6
                    elif msc_version >= 1700:
                        # VS2012/VC11
                        vc_version = 11
                    elif msc_version >= 1600:
                        # VS2010/VC10
                        vc_version = 10
                    elif msc_version >= 1500:
                        # VS2008/VC9
                        vc_version = 9

                except ValueError:
                    pass

            compiler_str = "_vc%d" % vc_version

        
        p4python_dir = "p4python_py%s_p4%s%s_%s" % (py_version_str, p4d_version_str, compiler_str, os_str)
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
            
            
            
            
  