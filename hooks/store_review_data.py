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
    
    def execute(self, local_path, review_data, **kwargs):
        """
        Store the specified publish data so that it can be retrieved lated by
        the corresponding load_publish_data hook
        
        :local_path:    String
                        Local path to the file being published
                        
        :review_data:   Dictionary
                        Dictionary of data to store for the review 'Version'.  This dictionary contains
                        the creation data for a Shotgun 'Version' entity

        """
        
        # The default implementation uploads any review files/movies to Shotgun.
        # 
        # The version data is then stored in a Perforce attribute on each published file
        # that the review should be associated with so that it can be retrieved by the
        # corresponding 'LoadReviewData' hook later.
        
        # nothing to do if there are no local publish paths or any version data!
        if not local_path or not review_data:
            return None

        p4_fw = self.parent
        from P4 import P4Exception

        # we'll need a Perforce connection:
        p4 = p4_fw.connection.connect()
        
        # we're going to store the version data with each published file the version
        # will ultimately be linked to.        
        sg_review_metadata = copy.deepcopy(review_data)

        # convert all local paths to depot paths:
        paths_to_convert = [local_path]
        local_path_to_frames = sg_review_metadata.get("sg_path_to_frames")
        if local_path_to_frames:
            paths_to_convert.append(local_path_to_frames)
        
        depot_paths = p4_fw.util.client_to_depot_paths(p4, paths_to_convert)
        
        depot_publish_path = depot_paths[0]
        depot_path_to_frames = depot_paths[1] if local_path_to_frames else None 

        # check that publish path translated ok:
        if not depot_publish_path:
            raise TankError("Failed to determine Perforce depot path for local file '%s'" % local_path)
            
        # handle sg_path_to_frames if set:
        if local_path_to_frames:
            if not depot_path_to_frames:
                raise TankError("Failed to determine Perforce depot path for local file '%s'" % local_path_to_frames)
            sg_review_metadata["sg_path_to_frames"] = depot_path_to_frames 
            
        # if we have an uploaded movie then upload it to shotgun:
        uploaded_movie_path = sg_review_metadata.get("sg_uploaded_movie")
        if uploaded_movie_path:
            del(sg_review_metadata["sg_uploaded_movie"])
            if os.path.exists(uploaded_movie_path):
                # upload movie:
                attachment_id = self.__upload_file_to_sg(uploaded_movie_path)
                sg_review_metadata["sg_uploaded_movie"] = (attachment_id, uploaded_movie_path)

        # store the review data as a Perforce attribute on the published file:
        #

        # dump to yaml string:
        sg_metadata_str = yaml.dump(sg_review_metadata)

        # update attribute for publish path:
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
        
        
        
        
        
        
        
        
        
        