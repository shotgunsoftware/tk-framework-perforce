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
import copy
 
class StorePublishData(sgtk.Hook):
    
    PUBLISH_ATTRIB_NAME = "shotgun_metadata"
    REVIEW_ATTRIB_NAME = "shotgun_review_metadata"
    
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
        
        # The default implementation stores the publish data in a p4 attribute so 
        # that it lives with the file:
        #
        #    shotgun_metadata - store a yaml version of all metadata
        #
        # If a thumbnail is specified in the publish_data then this is uploaded to
        # Shotgun as an attachment to the current project. 
        if not local_path or not publish_data:
            return
        
        sg_metadata = copy.deepcopy(publish_data)
                        
        p4_fw = self.parent
        p4_util = p4_fw.import_module("util")
        from P4 import P4Exception

        # we'll need a Perforce connection:
        p4 = p4_fw.connect()
        
        # convert dependencies from local to depot paths:
        dependency_paths = sg_metadata.get("dependency_paths", [])
        if dependency_paths:
            depot_dependency_paths = p4_util.client_to_depot_paths(p4, dependency_paths)
            depot_dependency_paths = [dp for dp in depot_dependency_paths if dp]
            sg_metadata["dependency_paths"] = depot_dependency_paths

        # replace context with a serialized version:
        ctx = sg_metadata.get("context")
        if ctx:
            ctx_str = sgtk.context.serialize(ctx)
            sg_metadata["context"] = ctx_str
        
        # store thumbnail as Project attachment in Shotgun:
        thumbnail_path = sg_metadata.get("thumbnail_path")
        if thumbnail_path and os.path.exists(thumbnail_path):
            attachment_id = self.__upload_file_to_sg(thumbnail_path)
            sg_metadata["thumbnail_path"] = (thumbnail_path, attachment_id)
            
        # format as yaml data:
        sg_metadata_str = yaml.dump(sg_metadata)
        
        # set the 'shotgun_metadata' attribute on the file in Perforce:
        try:
            # use '-p' to create a propogating attribute that will propogate with the file 
            # when the file is opened for add, edit or delete.  This will ensure subsequent
            # changes to the file retain this information unless it's modified by a future
            # publish
            p4.run_attribute("-p", "-n", StorePublishData.PUBLISH_ATTRIB_NAME, "-v", sg_metadata_str, local_path)
        except P4Exception, e:
            raise TankError("Failed to store publish data in Perforce attribute for file '%s'" % local_path)

        # clear the 'shotgun_review_metadata' attribute.  This handles the following
        # case where review data shouldn't be linked to the published file(s):
        #
        # 1. Publish with review - _don't_ commit to Perforce
        # 2. Publish _without_ review
        # 3. Commit to Perforce
        try:
            p4.run_attribute("-n", StorePublishData.REVIEW_ATTRIB_NAME, local_path)
        except P4Exception, e:
            raise TankError("Failed to clear review data in Perforce attribute for file '%s'" % local_path)


    def __upload_file_to_sg(self, file_path):
        """
        Upload the specified file to Shotgun as an attachment to the current project
        """
        # first check if the file has already been uploaded or not:
        if not hasattr(self.parent, "__sg_uploaded_file_cache"):
            self.parent.__sg_uploaded_file_cache = {}
        cache = self.parent.__sg_uploaded_file_cache
        
        file_size = os.path.getsize(file_path)
        file_mtime = os.path.getmtime(file_path)
        file_key = (file_path, file_size, file_mtime)
        
        attachment_id = cache.get(file_key)
        if attachment_id is not None:
            # file has previously been uploaded as an attachment
            # so just return the id:
            return attachment_id
        
        # upload file to shotgun, linking to the project:
        attachment_id = self.parent.shotgun.upload("Project", self.parent.context.project["id"], file_path)
        cache[file_key] = attachment_id
        
        # and update the attachment with a useful description:
        self.parent.shotgun.update("Attachment", attachment_id, {"description":"Perforce publish data"})
    
        return attachment_id
        


