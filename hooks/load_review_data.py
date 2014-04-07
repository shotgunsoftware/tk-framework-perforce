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
 
class LoadReviewData(sgtk.Hook):
    
    REVIEW_ATTRIB_NAME = "shotgun_review_metadata"
    
    def execute(self, depot_path, user, workspace, revision, p4, **kwargs):
        """
        Load the specified review data that was previously stored by
        the corresponding save_review_data hook
        
        :param depot_path:  String
                            Depot path to the file being published
                        
        :param user:        Dictionary
                            Shotgun HumanUser entity dictionary
                        
        :param workspace:   String
                            The Perforce workspace/client that path is being published in
                     
        :param revision:    Int
                            Revision of the file
                        
        :param p4:          P4 instance
                            The Perforce connection to use if needed.
                                                 
        :returns:           Dictionary
                            A dictionary containing the following entries:
                            {
                                "data":Dictionary         - this is the entity creation data for a Shotgun Version
                                                            entity that was stored by the corresponding store hook
                            
                                "temp_files":List         - this is a list of temporary files that can be deleted
                                                            once they are finished with by the calling bundle
                            }
        """
        # the default implementation looks for the review data in a p4 attribute 
        # that lives with the file:
        #
        #    shotgun_review_metadata - contains a yaml version of all metadata
        #
        # If a movie was specified in the review_data then this will have been
        # stored as a project attachment and will need to be downloaded.
        temp_files = []
        
        p4_fw = self.parent
        from P4 import P4Exception

        # make sure we have a Perforce connection:
        p4 = p4 if p4 else p4_fw.connection.connect()

        # get the attribute data from Perforce:        
        p4_attr_name = "attr-%s" % LoadReviewData.REVIEW_ATTRIB_NAME
        depot_revision_path = "%s#%d" % (depot_path, revision)
        file_details = p4_fw.util.get_depot_file_details(p4, depot_revision_path, fields = [p4_attr_name])
        
        # find data and load yaml data:
        sg_metadata_str = file_details[depot_revision_path].get(p4_attr_name)        
        sg_metadata = {}
        if sg_metadata_str:
            sg_metadata = yaml.load(sg_metadata_str)
        if not sg_metadata:
            return
        
        # download thumbnail from attachment in Shotgun:
        uploaded_movie_data = sg_metadata.get("sg_uploaded_movie")
        if uploaded_movie_data:
            attachment_id = 0
            file_suffix = None
            if isinstance(uploaded_movie_data, tuple):
                # data is an (id, path) tuple:
                attachment_id, path = uploaded_movie_data
                _, file_suffix = os.path.splitext(path)
            elif isinstance(uploaded_movie_data, int):
                attachment_id = uploaded_movie_data
                
                # get the path from Shotgun:
                sg_entity = self.parent.shotgun.find_one("Attachment", [["id", "is", attachment_id]], ["filename"])
                path = sg_entity.get("filename")
                _, file_suffix = os.path.splitext(path)
                
            if attachment_id:
                uploaded_movie_path = self.__download_file_from_sg(attachment_id, file_suffix)
                if uploaded_movie_path:
                    sg_metadata["sg_uploaded_movie"] = uploaded_movie_path
                    temp_files.append(uploaded_movie_path)
                else:
                    del(sg_metadata["sg_uploaded_movie"])

        return {"data":sg_metadata, "temp_files":temp_files}

        
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
        
        
        
        
        
        
        
        
        