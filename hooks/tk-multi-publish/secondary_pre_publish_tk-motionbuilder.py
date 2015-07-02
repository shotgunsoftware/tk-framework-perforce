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
import maya.cmds as cmds

import tank
from tank import Hook
from tank import TankError

class PrePublishHook(Hook):
    """
    Single hook that implements pre-publish functionality
    """
    def execute(self, tasks, work_template, progress_cb, **kwargs):
        """
        Main hook entry point
        :param tasks:           List of tasks to be pre-published.  Each task is be a 
                                dictionary containing the following keys:
                                {   
                                    item:   Dictionary
                                            This is the item returned by the scan hook 
                                            {   
                                                name:           String
                                                description:    String
                                                type:           String
                                                other_params:   Dictionary
                                            }
                                           
                                    output: Dictionary
                                            This is the output as defined in the configuration - the 
                                            primary output will always be named 'primary' 
                                            {
                                                name:             String
                                                publish_template: template
                                                tank_type:        String
                                            }
                                }
                        
        :param work_template:   template
                                This is the template defined in the config that
                                represents the current work file
               
        :param progress_cb:     Function
                                A progress callback to log progress during pre-publish.  Call:
                                
                                    progress_cb(percentage, msg)
                                     
                                to report progress to the UI
                        
        :returns:               A list of any tasks that were found which have problems that
                                need to be reported in the UI.  Each item in the list should
                                be a dictionary containing the following keys:
                                {
                                    task:   Dictionary
                                            This is the task that was passed into the hook and
                                            should not be modified
                                            {
                                                item:...
                                                output:...
                                            }
                                            
                                    errors: List
                                            A list of error messages (strings) to report    
                                }
        """       
        
        # TODO - implement this - look at the maya hook and at default mobu hook
        # https://github.com/shotgunsoftware/tk-multi-publish/blob/master/hooks/secondary_pre_publish_tk-motionbuilder.py

    
    
