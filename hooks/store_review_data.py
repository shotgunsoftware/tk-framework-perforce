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

import os
import sys
import copy

import sgtk
from sgtk import TankError
from tank_vendor import yaml
 
class StoreReviewData(sgtk.Hook):
    
    REVIEW_ATTRIB_NAME = "shotgun_review_metadata"
    
    def execute(self, local_publish_paths, version_data, **kwargs):
        """
        Store the specified publish data so that it can be retrieved lated by
        the corresponding load_publish_data hook
        
        :local_publish_paths:   
                        List(String)
                        Local paths to the (published) files that this review data should
                        be registered for.
                        
        :version_data:  Dictionary
                        Dictionary of data to store for the review 'Version'.  This dictionary contains
                        the creation data for a Shotgun 'Version' entity

        """
        
        # The default implementation uploads any review files/movies to Shotgun.
        # 
        # The version data is then stored in a Perforce attribute on each published file
        # that the review should be associated with so that it can be retrieved by the
        # corresponding 'LoadReviewData' hook later.
        
        # nothing to do if there are no local publish paths or any version data!
        if not local_publish_paths or not version_data:
            return None

        p4_fw = self.parent
        p4_util = p4_fw.import_module("util")
        from P4 import P4Exception

        # we'll need a Perforce connection:
        p4 = p4_fw.connect()
        
        # we're going to store the version data with each published file the version
        # will ultimately be linked to.        
        sg_review_metadata = copy.deepcopy(version_data)

        # we'll also need depot paths for all local paths:
        depot_publish_paths = p4_util.client_to_depot_paths(p4, local_publish_paths)
        for local, depot in zip(local_publish_paths, depot_publish_paths):
            if not depot:
                # (AD) - this doesn't handle new files!
                raise TankError("Failed to determine Perforce depot path for local file '%s'" % local)
        
        # iterate over review metadata:
        attachment_map = {}
        for item in sg_review_metadata:
            
            # add published file paths in to the data:
            item["published_files"] = depot_publish_paths
            
            # handle sg_path_to_frames if set:
            path_to_frames = item.get("sg_path_to_frames")
            if path_to_frames:
                # (TODO) convert to depot path:
                pass
            
            # upload any files to Shotgun and replace in data with attachment id's:
            # Q. are there other fields on the "Version" entity that may contain
            # files that need to be stored?
            review_file = item.get("sg_uploaded_movie")
            if review_file:
                attachment_id = None                
                if os.path.exists(review_file):
                    # have we already uploaded this movie:
                    attachment_id = attachment_map.get(review_file, None)
                    if attachment_id is None:
                        # upload:
                        attachment_id = self.__upload_file_to_sg(review_file)
                        attachment_map[review_file] = attachment_id
                item["sg_uploaded_movie"] = attachment_id

        # store the review data as a Perforce attribute on each published file:
        #
        
        # get any existing attribute information: 
        p4_openattr_name = "openattr-%s" % StoreReviewData.REVIEW_ATTRIB_NAME
        local_file_attribs = p4_util.get_client_file_details(p4, local_publish_paths, 
                                                             fields = [p4_openattr_name])

        # now update for each path:
        for local_path in local_publish_paths:
            
            # get any existing review data - we don't want to overwrite it:
            existing_review_metadata = []
            sg_metadata_str = local_file_attribs[local_path].get(p4_openattr_name)
            if sg_metadata_str:
                existing_review_metadata = yaml.load(sg_metadata_str)
    
            # add in new data:
            existing_review_metadata.append(sg_review_metadata)
    
            # dump to yaml string:
            sg_metadata_str = yaml.dump(existing_review_metadata)

            # and update attribute with new data:
            try:                
                p4.run_attribute("-n", StoreReviewData.REVIEW_ATTRIB_NAME, "-v", sg_metadata_str, local_path)
            except P4Exception, e:
                raise TankError("Failed to store review data in Perforce attribute for file '%s'" % local_path)
        
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
        self.parent.shotgun.update("Attachment", attachment_id, {"description":"Perforce review data"})
    
        return attachment_id
        
        
        
        
        
        
        
        
        
        