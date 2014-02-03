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
Hook that gets called to load publish data for a path submitted to Perforce
"""

import sgtk
from tank_vendor import yaml

import os
import sys
import tempfile
import binascii
 
class LoadPublishData(sgtk.Hook):
    
    def execute(self, depot_path, user, workspace, revision, **kwargs):
        """
        Load the specified publish data so that was previously stored by
        the corresponding save_publish_data hook
        
        :depot_path:    String
                        Depot path to the file being published
                        
        :user:          Dictionary
                        Shotgun HumanUser entity dictionary
                        
        :workspace:     String
                        The Perforce workspace/client that path is being published in
                     
        :revision:      Int
                        Revision of the file
                     
        :returns:       Dictionary
                        Dictionary of data loaded for the published file.  This data should match 
                        the parameters expected by the 'sgtk.util.register_publish()' function.
        """
        # the default implementation looks for the publish data in a p4 attribute 
        # that lives with the file:
        #
        #    shotgun_metadata - contains a yaml version of all metadata
        data = {}
        
        p4_fw = self.parent
        p4_util = p4_fw.import_module("util")
        from P4 import P4Exception

        # we'll need a Perforce connection:
        p4 = p4_fw.connect()

        sg_metadata = {}
        try:    
            p4_res = p4.run_fstat('-Oa', "%s#%d" % (depot_path, revision))
            if p4_res:
                sg_metadata_str = p4_res[0].get("attr-shotgun_metadata")
                if sg_metadata_str:
                    sg_metadata = yaml.load(sg_metadata_str)
        except P4Exception, e:
            return {}

        if not sg_metadata:
            return {}

        # build data dictionary to return:
        data["comment"] = sg_metadata.get("comment", "")
        data["dependency_paths"] = sg_metadata.get("dependency_paths", [])
        
        task = sg_metadata.get("task")
        if task:
            data["task"] = task

        entity = sg_metadata.get("entity")
        if entity:
            ctx = p4_fw.sgtk.context_from_entity(entity["type"], entity["id"])
            data["context"] = ctx

        data["published_file_type"] = sg_metadata.get("published_file_type")
            
        # thumbnail:
        if "thumbnail" in sg_metadata:
            
            thumbnail_str = sg_metadata["thumbnail"]
            content = binascii.unhexlify(thumbnail_str)
            thumbnail_sfx = sg_metadata.get("thumbnail_type", ".png")
            
            # have a thumbnail so save it to a temporary file:
            temp_file, thumbnail_path = tempfile.mkstemp(suffix=thumbnail_sfx, prefix="tanktmp")
            if temp_file:
                os.close(temp_file)
                
            f = open(thumbnail_path, "wb")
            try:
                f.write(content)
            finally:
                f.close()
                
            data["thumbnail_path"] = thumbnail_path
            
        return data
