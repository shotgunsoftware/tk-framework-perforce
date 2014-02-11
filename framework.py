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
    
    def connect(self, allow_ui=True, password=None):
        """
        Connect to Perforce
        """
        util = self.import_module("util")
        return util.ConnectionHandler(self).connect(allow_ui, password)
        
    def connect_with_dlg(self):
        """
        Show the Perforce connection dialog
        """
        util = self.import_module("util")
        return util.ConnectionHandler(self).connect_with_dlg()
    
    def get_perforce_user(self, sg_user):
        """
        Return the Perforce user associated with the specified Shotgun user
        """
        return self.execute_hook("hook_get_perforce_user", sg_user = sg_user)

    def get_shotgun_user(self, p4_user):
        """
        Return the Shotgun user associated with the specified Perforce user
        """
        return self.execute_hook("hook_get_shotgun_user", p4_user = p4_user)
        
        
    def store_publish_data(self, local_path, publish_data):
        """
        Store the publish data for the specified path somewhere using a hook
        """
        self.execute_hook("hook_store_publish_data", 
                          local_path = local_path,
                          publish_data = publish_data)
    
    def load_publish_data(self, depot_path, user, workspace, revision):
        """
        Load the publish data for the specified path, user & workspace
        from the location it was stored using a hook
        """
        return self.execute_hook("hook_load_publish_data", 
                                 depot_path = depot_path,
                                 user = user, 
                                 workspace = workspace,
                                 revision = revision)

    def store_publish_version_data(self, local_publish_paths, version_data):
        """
        Store review 'version' data for the specified publish paths
        somewhere using a hook
        """
        self.execute_hook("hook_store_review_data", 
                          local_publish_paths = local_publish_paths,
                          version_data = version_data)

    def load_publish_review_data(self, depot_path, user, workspace, revision):
        """
        Load the review version data for the specified publish paths, user & workspace
        from the location it was stored using a hook
        """
        return self.execute_hook("hook_load_review_data", 
                                 depot_path = depot_path,
                                 user = user, 
                                 workspace = workspace,
                                 revision = revision)

        
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
        
        # Perforce server version:
        #
        # The version of P4Python required to work with a Perforce server version
        # is a bit random!  Ideally it should be the same version but a different
        # version may work without problems depending on API changes and required
        # functionality.
        #
        # The following code attempts to find the most suitable version from the
        # available versions for the server version specified in the config  
        p4d_version = self.get_setting("server_version")
        supported_versions = [2012.1]#, 2013.1]
        if p4d_version not in supported_versions:
            # no exact match found so look for highest version matching
            # major version only:
            supported_versions.sort(reverse=True)
            matching_version = None    
            for v in supported_versions:
                # check if the version is in range: 
                if int(p4d_version) <= v <= p4d_version:
                    matching_version = v 
                    break
                
            # use this version or default to the latest available version:
            p4d_version = matching_version or supported_versions[0]
        
        p4d_version_str = ("%f" % p4d_version).rstrip("0")
        
        # platform/os string
        os_str = {"darwin":"mac", "win32":"win64" if sys.maxsize > 2**32 else "win32", "linux2":"linux"}[sys.platform]
        
        # compiler string - currently windows specific:
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
                    
                    # convert this to a vc version - follow convention of 
                    # msc_version being 6 ahead of vc version!
                    vc_version = msc_version/100 - 6
                    
                except ValueError:
                    pass

            compiler_str = "_vc%d" % vc_version

        # build the python directory:
        p4python_dir = "p4python_py%s_p4d%s%s_%s" % (py_version_str, p4d_version_str, compiler_str, os_str)
        p4_path = os.path.join(self.disk_location, "resources", p4python_dir, "python")
        if not os.path.exists(p4_path):
            self.log_error("Unable to locate a compatible version of P4Python for Python v%d.%d, P4D v%s%s. "
                           "Please contact toolkitsupport@shotgunsoftware.com for assistance!" 
                           % (sys.version_info[0], sys.version_info[1], p4d_version_str, compiler_str))
        else:
            sys.path.append(p4_path)
                
            # finally, check that it's working!
            try:
                from P4 import P4
            except:
                self.log_error("Failed to load P4Python!")
            else:
                self.log_debug("P4Python successfully loaded!")
            
            
  