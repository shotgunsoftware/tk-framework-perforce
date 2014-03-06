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

This example uses a Shotgun custom entity as a storage location for Publish Data.

The 'Pending Published File' entity should be set up with the following fields:

    # Entity used to store publish data between publish & perforce->shotgun sync
    PENDING_PUBLISHED_FILE_ENTITY: [
        {"display_name": "Workspace",            "type":"text",          "properties":{}},
        {"display_name": "Published File Type",  "type":"text",          "properties":{}},
        {"display_name": "Entity",               "type":"entity",        "properties":{"valid_types": ["Asset", LEVEL_ENTITY]}},
        {"display_name": "Task",                 "type":"entity",        "properties":{"valid_types": ["Task"]}},
        {"display_name": "Metadata",             "type":"url",           "properties":{}},
        {"display_name": "Head Revision",        "type":"number",        "properties":{}}            
    ]
    
    # Note: LEVEL_ENTITY should be set to the custom entity being used to represent
    # levels

The custom entity should be updated in the code below and in the corresponding
store_publish_data_shotgun.py hook.
"""

import sgtk
from tank_vendor import yaml

import os 
import sys
import urllib
import tempfile

# TODO: set this to the custom entity set up to represent pending published files
PENDING_PUBLISHED_FILE_ENTITY = "CustomEntity27"
 
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
        p4_fw = self.parent

        # we'll need a Perforce connection:
        p4 = p4_fw.connection.connect()
        
        # look for a PendingPublishedFile entity in Shotgun that matches the depot path, workspace & user
        filters = [["project", "is", p4_fw.context.project],
                   ["code", "is", depot_path], 
                   ["created_by", "is", user],
                   ["sg_workspace", "is", workspace],
                   ["sg_head_revision", "less_than", revision]]
        fields = ["description", "sg_published_file_type", "sg_entity", "sg_task", "image", "sg_metadata"]
        
        # return the most recent data for the head revision before the specified revision:
        order_by = [{"field_name":"sg_head_revision", "direction":"desc"}, {"field_name":"created_at", "direction":"desc"}]

        sg_res = p4_fw.shotgun.find_one(PENDING_PUBLISHED_FILE_ENTITY, filters = filters, fields = fields, order = order_by)
        if not sg_res:
            # no record so stop now!
            return {}
        
        # build data dictionary to return:
        data = {}
        data["comment"] = sg_res.get("description")
        data["task"] = sg_res.get("sg_task")
        data["published_file_type"] = sg_res.get("sg_published_file_type")
        entity = sg_res.get("sg_entity")
        if entity:
            ctx = p4_fw.sgtk.context_from_entity(entity["type"], entity["id"])
            data["context"] = ctx
            
        # thumbnail - for the moment we're going to download it and re-upload it
        # as this fits with the register_publish interface.  This could be optimised
        # in the future though to just share it between entities:
        thumbnail_url = sg_res.get("image")
        if thumbnail_url:
            # download the thumbnail:
            try:
                temp_file, _ = urllib.urlretrieve(thumbnail_url)
            except Exception, e:
                #self._app.log_info("Could not download data from the url '%s'. Error: %s" % (url, e))
                pass
            else:
                data["thumbnail_path"] = temp_file
            
        # metadata:
        metadata_attachment = sg_res.get("sg_metadata")
        if metadata_attachment and metadata_attachment.get("type") == "Attachment" and "id" in metadata_attachment:
            # download the metadata file:
            # (TODO) - update when api is updated to support full attachment
            # dictionary
            attachment_id = metadata_attachment["id"] 
            file_data = self.parent.shotgun.download_attachment(attachment_id)
            
            metadata = yaml.load(file_data)
            data["dependency_paths"] = metadata.get("dependency_paths", [])
        
        return data

        
        
        