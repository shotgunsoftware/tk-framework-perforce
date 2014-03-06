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
from tank_vendor.shotgun_api3 import ShotgunFileDownloadError

import os
import sys
import tempfile
import binascii
 
class LoadPublishData(sgtk.Hook):
    
    PUBLISH_ATTRIB_NAME = "shotgun_metadata"
    
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
        #
        # If a thumbnail was specified in the publish_data then this will have been
        # stored as a project attachment and will need to be downloaded.         
        p4_fw = self.parent
        from P4 import P4Exception

        # we'll need a Perforce connection:
        p4 = p4_fw.connection.connect()

        # get the attribute data from Perforce:        
        p4_attr_name = "attr-%s" % LoadPublishData.PUBLISH_ATTRIB_NAME
        depot_revision_path = "%s#%d" % (depot_path, revision)
        file_details = p4_fw.util.get_depot_file_details(p4, depot_revision_path, fields = [p4_attr_name])
        
        # find data and load yaml data:
        sg_metadata_str = file_details[depot_revision_path].get(p4_attr_name)        
        sg_metadata = {}
        if sg_metadata_str:
            sg_metadata = yaml.load(sg_metadata_str)
        if not sg_metadata:
            return {}

        # replace context string with full context:
        ctx_str = sg_metadata.get("context")
        if ctx_str:
            ctx = sgtk.context.deserialize(ctx_str)
            sg_metadata["context"] = ctx
            
        # download thumbnail from attachment in Shotgun:
        thumbnail_path_data = sg_metadata.get("thumbnail_path")
        
        if thumbnail_path_data and isinstance(thumbnail_path_data, tuple):
            thumbnail_path, attachment_id = thumbnail_path_data

            # extract suffix from thumbnail_path:
            thumbnail_suffix = ".png"
            if thumbnail_path:
                _, thumbnail_suffix = os.path.splitext(thumbnail_path)

            # and download thumbnail:                
            thumbnail_path = self.__download_file_from_sg(attachment_id, thumbnail_suffix)
            if thumbnail_path:
                sg_metadata["thumbnail_path"] = thumbnail_path
            else:
                del sg_metadata["thumbnail_path"]                

        return sg_metadata 

    def __download_file_from_sg(self, attachment_id, suffix):
        """
        """
        # first check if the file has already been downloaded or not:
        if not hasattr(self.parent, "__sg_downloaded_attachment_cache"):
            self.parent.__sg_downloaded_attachment_cache = {}
        cache = self.parent.__sg_downloaded_attachment_cache
        
        file_path = cache.get(attachment_id)
        if file_path and os.path.exists(file_path):
            # we've already downloaded it so just return path:
            return file_path
        
        # get a temp path to write out to:
        temp_file, temp_path = tempfile.mkstemp(suffix=suffix, prefix="shotguntmp")
        if temp_file:
            os.close(temp_file)
        
        # using old API so can't write straight to file - consider updating!
        try:
            self.parent.shotgun.download_attachment(attachment_id=attachment_id, file_path=temp_path)
        except ShotgunFileDownloadError:
            # we'll just ignore the error for the time being and let the calling
            # code deal with no path being returned!
            return

        return temp_path    


