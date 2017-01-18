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
        """
        Construction
        """
        self.log_debug("%s: Initializing..." % self)
        
        # initialize p4python:
        self.__init_p4python()
        
        # add modules to this instance so the interface is nicer for users
        # allows fw.util type syntax.
        self.connection = self.import_module("connection")
        self.util = self.import_module("util")
        self.widgets = self.import_module("widgets")
        
        self.__p4_to_sg_user_map = {}
        self.__sg_to_p4_user_map = {}
    
    def destroy_framework(self):
        """
        Destruction
        """
        self.log_debug("%s: Destroying..." % self)
    
    # Username handling (via hooks)
    #
    def get_perforce_user(self, sg_user):
        """
        Return the Perforce user associated with the specified Shotgun user
        """
        if sg_user["id"] in self.__sg_to_p4_user_map: 
            return self.__sg_to_p4_user_map[sg_user["id"]]
        
        p4_user = self.execute_hook("hook_get_perforce_user", sg_user = sg_user)
        self.__sg_to_p4_user_map[sg_user["id"]] = p4_user
        return p4_user

    def get_shotgun_user(self, p4_user):
        """
        Return the Shotgun user associated with the specified Perforce user
        """
        if p4_user in self.__p4_to_sg_user_map: 
            return self.__p4_to_sg_user_map[p4_user]
        
        sg_user = self.execute_hook("hook_get_shotgun_user", p4_user = p4_user)
        self.__p4_to_sg_user_map[p4_user] = sg_user
        return sg_user
        
    # store/load publish data
    #
    def store_publish_data(self, local_path, publish_data, p4=None):
        """
        Store the publish data for the specified path somewhere using a hook
        """
        self.execute_hook("hook_store_publish_data", 
                          local_path = local_path,
                          publish_data = publish_data,
                          p4 = p4)
    
    def load_publish_data(self, depot_path, user, workspace, revision, p4=None):
        """
        Load the publish data for the specified path, user & workspace
        from the location it was stored using a hook
        """
        return self.execute_hook("hook_load_publish_data", 
                                 depot_path = depot_path,
                                 user = user, 
                                 workspace = workspace,
                                 revision = revision,
                                 p4 = p4)

    # store/load review data
    #
    def store_publish_review_data(self, local_path, review_data, p4=None):
        """
        Store review 'version' data for the specified publish path
        somewhere using a hook
        """
        self.execute_hook("hook_store_review_data", 
                          local_path = local_path,
                          review_data = review_data,
                          p4 = p4)

    def load_publish_review_data(self, depot_path, user, workspace, revision, p4=None):
        """
        Load the review version data for the specified publish paths, user & workspace
        from the location it was stored using a hook
        """
        return self.execute_hook("hook_load_review_data", 
                                 depot_path = depot_path,
                                 user = user, 
                                 workspace = workspace,
                                 revision = revision,
                                 p4 = p4)

    # private methods
    #    
    def __init_p4python(self):
        """
        Make sure that p4python is available and if it's not then add it to the path if 
        we have a version we can use.
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

        # build the directory path for our distributed P4Python:
        #
        
        # Python version:
        py_version_str = "%d%d" % (sys.version_info[0], sys.version_info[1])

        # platform/os string
        os_str = {"darwin":"mac", "win32":"win64" if sys.maxsize > 2**32 else "win32", "linux2":"linux"}[sys.platform]
        
        # compiler string - currently windows specific
        compiler_strings = [""]
        preferred_compiler_str = ""
        if sys.platform == "win32":
            # For windows, we may need to determine p4python based on compiler.  Note that the compiler information
            # obtained from the platform module will only be correct when using python.exe or an embedded python dll
            # that was built with the same compiler as the containing executable.
            #
            # Because of this, we find the preferred compiler based on the version used to build Python but then
            # we also have to fall back to try and load versions built with other compilers if this fails.
            #
            # The main example of this atm is 3ds Max 2014 with Blur Python running Python 2.7...  3ds Max & Blur
            # are both compiled with VS 2010 but the stock release of Python 2.7 is built with VS 2008.
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
                    
                    # convert this to a vc version - follow convention of 
                    # msc_version being 6 ahead of vc version!
                    vc_version = msc_version/100 - 6
                    
                except ValueError:
                    pass

            preferred_compiler_str = "_vc%d" % vc_version
            compiler_strings = [preferred_compiler_str]
            # add in all other versions we support:
            for v in [9, 10]:
                if v != vc_version:
                    compiler_strings.append("_vc%d" % v)

        # attempt to import P4:
        loaded_p4 = False
        preferred_p4_path = ""
        for compiler_str in compiler_strings:
            p4python_dir = "p4python_py%s%s_%s" % (py_version_str, compiler_str, os_str)
            p4_path = os.path.join(self.disk_location, "resources", p4python_dir, "python")
            if compiler_str == preferred_compiler_str:
                preferred_p4_path = p4_path

            # append it to the path:
            if p4_path not in sys.path: 
                sys.path.append(p4_path)
            try:
                # attempt to import P4
                from P4 import P4
            except:
                # failed to load so lets remove it from the path!
                if sys.path[-1] == p4_path:
                    del sys.path[-1]
            else:
                loaded_p4 = True
                break

        if not loaded_p4:
            if not os.path.exists(preferred_p4_path):
                self.log_error("Unable to locate a compatible version of P4Python for Python v%d.%d%s. "
                               "Please contact support@shotgunsoftware.com for assistance!" 
                               % (sys.version_info[0], sys.version_info[1], preferred_compiler_str))
            else:            
                self.log_error("Failed to load P4Python!")
        else:
            self.log_debug("P4Python successfully loaded!")
            
  