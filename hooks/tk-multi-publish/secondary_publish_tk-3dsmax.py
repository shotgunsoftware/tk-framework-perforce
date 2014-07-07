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
import shutil
from Py3dsMax import mxs

import sgtk
from sgtk import Hook
from sgtk import TankError

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

class PublishHook(Hook):
    """
    Single hook that implements publish functionality for secondary tasks
    """    
    def execute(self, tasks, work_template, comment, thumbnail_path, sg_task, primary_task, primary_publish_path, progress_cb, **kwargs):
        """
        Main hook entry point
        :param tasks:                   List of secondary tasks to be published.  Each task is a 
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
                        
        :param work_template:           template
                                        This is the template defined in the config that
                                        represents the current work file
               
        :param comment:                 String
                                        The comment provided for the publish
                        
        :param thumbnail:               Path string
                                        The default thumbnail provided for the publish
                        
        :param sg_task:                 Dictionary (shotgun entity description)
                                        The shotgun task to use for the publish    
                        
        :param primary_publish_path:    Path string
                                        This is the path of the primary published file as returned
                                        by the primary publish hook
                        
        :param progress_cb:             Function
                                        A progress callback to log progress during pre-publish.  Call:
                                        
                                            progress_cb(percentage, msg)
                                             
                                        to report progress to the UI
                        
        :param primary_task:            The primary task that was published by the primary publish hook.  Passed
                                        in here for reference.  This is a dictionary in the same format as the
                                        secondary tasks above.
        
        :returns:                       A list of any tasks that had problems that need to be reported 
                                        in the UI.  Each item in the list should be a dictionary containing 
                                        the following keys:
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
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        
        # open a connection to Perforce:
        p4 = p4_fw.connection.connect()
        
        # find the changelist containing the primary publish file that was 
        # created during the primary publish phase.
        primary_change = primary_task["item"].get("other_params", {}).get("p4_change")
        
        results = []
        
        # we want to keep track of all files being published
        # so that we can add them to the Perforce change at 
        # the end.
        secondary_publish_files = []
        p4_submit_task = None
        
        # publish all tasks except the "p4_submit" task:
        for task in tasks:
            item = task["item"]
            output = task["output"]
            errors = []
        
            if output["name"] == "p4_submit":
                # we'll handle this later:
                p4_submit_task = task
                continue
        
            # report progress:
            progress_cb(0, "Publishing", task)
        
            # publish item here, e.g.
            #if output["name"] == "...":
            #    # do the actual publish...
            #    ...
            #    # add secondary publish file to the change:        
            #    if primary_change != None:
            #        p4_fw.util.add_to_change(p4, primary_change, secondary_publish_path)
            #
            #    # store additional metadata for the publish:
            #    publish_data = {"thumbnail_path":thumbnail_path,
            #                    "dependency_paths":[primary_publish_path],
            #                    "task":sg_task,
            #                    "comment":comment,
            #                    "context":self.parent.context,
            #                    "published_file_type":output["tank_type"]
            #                    }
            #    
            #    user = sgtk.util.get_current_user(self.parent.sgtk)
            #    p4_fw.store_publish_data(scene_path, user, p4.client, publish_data)
            #    ...
            #else:
            # don't know how to publish this output types!
            errors.append("Don't know how to publish this item!")   

            # if there is anything to report then add to result
            if len(errors) > 0:
                # add result:
                results.append({"task":task, "errors":errors})
             
            progress_cb(100)
            
        # now, if we need to, lets commit the change to perforce:
        if p4_submit_task:
            errors = []
            
            progress_cb(0, "Publishing", task)
            
            if primary_change is None:
                errors.append("Failed to find the Perforce change containing the file '%s'" % primary_publish_path)
            else:
                progress_cb(10, "Submitting change '%s'" % primary_change)
                p4_fw.util.submit_change(p4, primary_change)
                
            # if there is anything to report then add to result
            if len(errors) > 0:
                # add result:
                results.append({"task":p4_submit_task, "errors":errors})        
                
            progress_cb(100)
             
        return results




        




