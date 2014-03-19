# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import sgtk
from sgtk import Hook
from sgtk import TankError

class PostPublishHook(Hook):
    """
    Single hook that implements post-publish functionality
    """    
    def execute(self, work_template, primary_task, secondary_tasks, progress_cb, **kwargs):
        """
        Main hook entry point
        
        :work_template: template
                        This is the template defined in the config that
                        represents the current work file

        :primary_task:  The primary task that was published by the primary publish hook.  Passed
                        in here for reference.

        :secondary_tasks:  The list of secondary taskd that were published by the secondary 
                        publish hook.  Passed in here for reference.
                        
        :progress_cb:   Function
                        A progress callback to log progress during pre-publish.  Call:
                        
                            progress_cb(percentage, msg)
                             
                        to report progress to the UI

        :returns:       None - raise a TankError to notify the user of a problem
        """
        # Note, if the commit to Perforce should always be done at the end of the publish
        # then it could make sense to move it here rather than having it as a secondary
        # output.
        #
        # If this is the case then the change id of the change to commit can be accessed
        # from the primary_task by doing:
        #
        # change = primary_task["item"].get("other_params", {}).get("p4_change")
        
        # The default implementation doesn't need to do anything here!
        return






        
        
