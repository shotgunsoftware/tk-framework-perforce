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
    
    def execute(self, local_path, publish_data, **kwargs):
        """
        Store the specified publish data so that it can be retrieved lated by
        the corresponding load_publish_data hook
        
        :local_path:    String
                        Local path to the file being published
                        
        :publish_data:  Dictionary
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
        dependency_paths = publish_data.get("dependency_paths", [])
        depot_dependency_paths = []
        if dependency_paths:
            depot_dependency_paths = p4_util.client_to_depot_paths(p4, dependency_paths)
            depot_dependency_paths = [dp for dp in depot_dependency_paths if dp]

        sg_metadata["dependency_paths"] = depot_dependency_paths
        
        # entity & task:
        task = publish_data.get("task")
        ctx = publish_data.get("context")
        if ctx:
            if ctx.entity:
                sg_metadata["entity"] = ctx.entity
            if not task:
                task = ctx.task
        if task:
            sg_metadata["task"] = task        
        
        # comment/description:
        sg_metadata["comment"] = publish_data.get("comment", "")
        
        # published file type:
        sg_metadata["published_file_type"] = publish_data.get("published_file_type", "")
        
        # thumbnail:
        thumbnail_path = publish_data.get("thumbnail_path")
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
                
        # format as yaml data:
        sg_metadata_str = yaml.dump(sg_metadata)
        
        # set the 'shotgun_metadata' attribute on the file in Perforce:
        try:
            # use '-p' to create a propogating attribute that will propogate with the file 
            # when the file is opened for add, edit or delete.  This will ensure subsequent
            # changes to the file retain this information unless it's modified by a future
            # publish
            p4.run_attribute("-p", "-n", "shotgun_metadata", "-v", sg_metadata_str, local_path)
        except P4Exception, e:
            raise TankError("Failed to store publish data in Perforce attribute for file '%s'" % local_path)

        # clear the 'shotgun_review_metadata' attribute.  This handles the following
        # case where review data shouldn't be linked to the published file(s):
        #
        # 1. Publish with review
        # 2. Publish _without_ review
        # 3. Commit to Perforce
        try:
            p4.run_attribute("-n", "shotgun_review_metadata", local_path)
        except P4Exception, e:
            raise TankError("Failed to clear review data in Perforce attribute for file '%s'" % local_path)
            
        
        


