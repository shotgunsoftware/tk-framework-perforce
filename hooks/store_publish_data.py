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
Hook that gets called to store publish data for a path being submitted to Perforce
"""

import sgtk
from tank_vendor import yaml

import os
import sys
import tempfile
import binascii
 
class StorePublishData(sgtk.Hook):
    
    def execute(self, local_path, user, workspace, data, **kwargs):
        """
        Store the specified publish data so that it can be retrieved lated by
        the corresponding load_publish_data hook
        
        :local_path:    String
                        Local path to the file being published
                        
        :user:          Dictionary
                        Shotgun HumanUser entity dictionary
                        
        :workspace:     String
                        The Perforce workspace/client that path is being published in                     

        :data:          Dictionary
                        Dictionary of data to store for the published file.  This data will match the
                        parameters expected by the 'sgtk.util.register_publish()' function.
        """
        
        # the default implementation stores the publish data in a p4 attribute so 
        # that it lives with the file:
        #
        #    shotgun_metadata - store a yaml version of all metadata
        sg_metadata = {}
                        
        p4_fw = self.parent
        p4_util = p4_fw.import_module("util")
        from P4 import P4Exception

        # we'll need a Perforce connection:
        p4 = p4_fw.connect()
        
        # dependencies:
        dependency_paths = data.get("dependency_paths", [])
        p4_file_details = p4_util.get_client_file_details(p4, dependency_paths)
        depot_dependency_paths = []
        for dp in dependency_paths:
            ddp = p4_file_details[dp].get("depotFile")
            if ddp:
                # only care about dependency paths that have valid depot paths
                # (TODO) - maybe this should error?
                depot_dependency_paths.append(ddp)

        sg_metadata["dependency_paths"] = depot_dependency_paths
        
        # entity & task:
        task = data.get("task")
        ctx = data.get("context")
        if ctx:
            if ctx.entity:
                sg_metadata["entity"] = ctx.entity
            if not task:
                task = ctx.task
        if task:
            sg_metadata["task"] = task        
        
        # comment/description:
        sg_metadata["comment"] = data.get("comment", "")
        
        # published file type:
        sg_metadata["published_file_type"] = data.get("published_file_type", "")
        
        # thumbnail:
        thumbnail_path = data.get("thumbnail_path")
        if thumbnail_path and os.path.exists(thumbnail_path):
            f = None
            try:
                f = open(thumbnail_path, "rb")
                content = f.read()
                _, sg_metadata["thumbnail_type"] = os.path.splitext(thumbnail_path)
                sg_metadata["thumbnail"] = binascii.hexlify(content)
            finally:
                if f:
                    f.close()
                
        # now format as yaml data:
        sg_metadata_str = yaml.dump(sg_metadata)
        
        #print "sg_metadata_str"
        #print sg_metadata_str
        
        # and finally, set it on the file in Perforce:
        try:
            # use '-p' to create a propogating attribute that will propogate with the file 
            # when the file is opened for add, edit or delete.  This will ensure subsequent
            # changes to the file retain this information unless it's modified by a future
            # publish
            p4.run_attribute("-p", "-n", "shotgun_metadata", "-v", sg_metadata_str, local_path)
        except P4Exception, e:
            raise TankError("Failed to store publish data in Perforce attribute for file '%s'" % local_path)


