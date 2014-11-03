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

import sgtk
from sgtk import Hook
from sgtk import TankError

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

class PrimaryPrePublishHook(Hook):
    """
    Single hook that implements pre-publish of the primary task
    """    
    def execute(self, task, work_template, progress_cb, **kwargs):
        """
        Main hook entry point
        :param task:            Primary task to be pre-published.  This is a
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

        :returns:               List 
                                A list of non-critical problems that should be 
                                reported to the user but not stop the publish.
                        
        :raises:                Hook should raise a TankError if the primary task
                                can't be published!
        """
        
        # get the engine name from the parent object (app/engine/etc.)
        engine_name = self.parent.engine.name
        
        # depending on engine:
        if engine_name == "tk-3dsmax":
            return self._do_3dsmax_pre_publish(task, work_template, progress_cb)
        if engine_name == "tk-3dsmaxplus":
            return self._do_3dsmaxplus_pre_publish(task, work_template, progress_cb)
        elif engine_name == "tk-maya":
            return self._do_maya_pre_publish(task, work_template, progress_cb)
        elif engine_name == "tk-photoshop":
            return self._do_photoshop_pre_publish(task, work_template, progress_cb)        
        else:
            raise TankError("Unable to perform pre-publish for unhandled engine %s" % engine_name)            
            
    def _do_3dsmax_pre_publish(self, task, work_template, progress_cb):
        """
        Do 3ds Max primary pre-publish/scene validation
        
        :param task:            The primary task to pre-publish
        :param work_template:   The template that matches the current work file
        :param progress_cb:     The progress callback to report all progress through
        
        :returns:               A list of strings representing any non-critical problems that 
                                were found during pre-processing.
        """
        from Py3dsMax import mxs
        
        progress_cb(0.0, "Validating current scene", task)
        
        # get the current scene file:
        scene_file = os.path.abspath(os.path.join(mxs.maxFilePath, mxs.maxFileName))
            
        progress_cb(25)
            
        # validate the work path:
        if not work_template.validate(scene_file):
            raise TankError("File '%s' is not a valid work path, unable to publish!" % scene_file)
        
        # Do any additional validation of the scene/primary task:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        p4 = p4_fw.connection.connect()
        p4_fw.util.open_file_for_edit(p4, scene_file, test_only=True)            
        
        progress_cb(100)
          
        return [] # no errors
            
    def _do_3dsmaxplus_pre_publish(self, task, work_template, progress_cb):
        """
        Do 3ds Max with MaxPlus primary pre-publish/scene validation
        
        :param task:            The primary task to pre-publish
        :param work_template:   The template that matches the current work file
        :param progress_cb:     The progress callback to report all progress through
        
        :returns:               A list of strings representing any non-critical problems that 
                                were found during pre-processing.
        """
        import MaxPlus
        
        progress_cb(0.0, "Validating current scene", task)
        
        # get the current scene file:
        scene_path = MaxPlus.FileManager.GetFileNameAndPath()
            
        progress_cb(25)
            
        # validate the work path:
        if not work_template.validate(scene_file):
            raise TankError("File '%s' is not a valid work path, unable to publish!" % scene_file)
        
        # Do any additional validation of the scene/primary task:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        p4 = p4_fw.connection.connect()
        p4_fw.util.open_file_for_edit(p4, scene_file, test_only=True)            
        
        progress_cb(100)
          
        return [] # no errors
    def _do_maya_pre_publish(self, task, work_template, progress_cb):
        """
        Do Maya primary pre-publish/scene validation
        
        :param task:            The primary task to pre-publish
        :param work_template:   The template that matches the current work file
        :param progress_cb:     The progress callback to report all progress through
        
        :returns:               A list of strings representing any non-critical problems that 
                                were found during pre-processing.        
        """
        import maya.cmds as cmds
        
        progress_cb(0.0, "Validating current scene", task)
        
        # get the current scene file:
        scene_file = cmds.file(query=True, sn=True)
        if scene_file:
            scene_file = os.path.abspath(scene_file)
        
        progress_cb(25)
            
        # validate the work path:
        if not work_template.validate(scene_file):
            raise TankError("File '%s' is not a valid work path, unable to publish!" % scene_file)
        
        # Do any additional validation of the scene/primary task:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        p4 = p4_fw.connection.connect()
        p4_fw.util.open_file_for_edit(p4, scene_file, test_only=True)
        
        progress_cb(100)
          
        return [] # no errors
        
    def _do_photoshop_pre_publish(self, task, work_template, progress_cb):
        """
        Do Photoshop primary pre-publish/scene validation
        
        :param task:            The primary task to pre-publish
        :param work_template:   The template that matches the current work file
        :param progress_cb:     The progress callback to report all progress through
        
        :returns:               A list of strings representing any non-critical problems that 
                                were found during pre-processing.        
        """
        import photoshop
        
        progress_cb(0.0, "Validating current scene", task)
        
        # get the current scene file:
        doc = photoshop.app.activeDocument
        if doc is None:
            raise TankError("There is no currently active document!")
        
        scene_file = doc.fullName.nativePath
            
        # validate the work path:
        if not work_template.validate(scene_file):
            raise TankError("File '%s' is not a valid work path, unable to publish!" % scene_file)
        
        # Do any additional validation of the scene/primary task:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        p4 = p4_fw.connection.connect()
        p4_fw.util.open_file_for_edit(p4, scene_file, test_only=True)
        
        progress_cb(100)
          
        return [] # no errors
        
