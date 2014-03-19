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
Hook that loads defines all the available actions, broken down by publish type. 
"""
import sgtk
import os

import pymel.core as pm
import maya.cmds as cmds

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"

HookBaseClass = sgtk.get_hook_baseclass()

class MayaActions(HookBaseClass):
    
    ##############################################################################################################
    # public interface - to be overridden by deriving classes 
    
    def generate_actions(self, sg_publish_data, actions, ui_area):
        """
        Returns a list of action instances for a particular publish.
        This method is called each time a user clicks a publish somewhere in the UI.
        The data returned from this hook will be used to populate the actions menu for a publish.
    
        The mapping between Publish types and actions are kept in a different place
        (in the configuration) so at the point when this hook is called, the loader app
        has already established *which* actions are appropriate for this object.
        The hook should return at least one action for each item passed in via the 
        actions parameter.
        
        This method needs to return detailed data for those actions, in the form of a list
        of dictionaries, each with name, params, caption and description keys.
        
        Because you are operating on a particular publish, you may tailor the output 
        (caption, tooltip etc) to contain custom information suitable for this publish.
        
        The ui_area parameter is a string and indicates where the publish is to be shown. 
        - If it will be shown in the main browsing area, "main" is passed. 
        - If it will be shown in the details area, "details" is passed.
        - If it will be shown in the history area, "history" is passed. 
        
        Please note that it is perfectly possible to create more than one action "instance" for 
        an action! You can for example do scene introspection - if the action passed in 
        is "character_attachment" you may for example scan the scene, figure out all the nodes
        where this object can be attached and return a list of action instances:
        "attach to left hand", "attach to right hand" etc. In this case, when more than 
        one object is returned for an action, use the params key to pass additional 
        data into the run_action hook.
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_publish_data))

        if ui_area == "history":
            # don't support loading previous versions!
            return []
        
        action_instances = []
                
        if "reference" in actions:
            action_instances.append( {"name": "reference", 
                                      "params": None,
                                      "caption": "Create Reference", 
                                      "description": "This will add the item to the scene as a standard reference."} )

        if "texture_node" in actions:        
            action_instances.append( {"name": "texture_node",
                                      "params": None, 
                                      "caption": "Create texture node", 
                                      "description": "Creates a file texture node for the selected item.."} )        
    
        return action_instances
                

    def execute_action(self, name, params, sg_publish_data):
        """
        Execute a given action, as enumerated by the create_actions() method.
        """
        app = self.parent
        app.log_debug("Execute action called for action %s. "
                      "Parameters: %s. Publish Data: %s" % (name, params, sg_publish_data))

        # open a perforce connection:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        
        p4 = p4_fw.connection.connect()
        if not p4:
            raise TankError("Failed to connect to Perforce!")
        
        # depot path is stored in the path as a url:
        p4_url =  sg_publish_data.get("path", {}).get("url")
            
        # convert from perforce url, validating server:
        path_and_revision = p4_fw.util.depot_path_from_url(p4_url)
        depot_path = path_and_revision[0] if path_and_revision else None
        if not depot_path:
            # either an invalid path or different server so skip
            raise TankError("Failed to determine Perforce file revision for url %s" % p4_url)
        
        if isinstance(depot_path, unicode):
            depot_path = depot_path.encode("utf8")
        
        # get local path:
        file_path = p4_fw.util.depot_to_client_paths(p4, [depot_path])[0]
        if not file_path:
            raise TankError("Failed to find local path for Perforce depot path %s" % depot_path)
        
        # make sure we have the latest revision synced (Note, this will handle dependencies in the future):
        p4_fw.util.sync_published_file(p4, sg_publish_data)

        if not os.path.exists(file_path):
            self.parent.log_warning("File not found on disk - '%s'" % file_path)

        if name == "reference":
            self._create_reference(file_path, sg_publish_data)
        
        if name == "texture_node":
            self._create_texture_node(file_path)
                        
           
    ##############################################################################################################
    # default implementation helpers
                   
    def _create_reference(self, file_path, sg_publish_data):
        # make a name space out of entity + name
        # e.g. bunny_upperbody
        namespace = "%s_%s" % (sg_publish_data.get("entity").get("name"), sg_publish_data.get("name"))   
        pm.system.createReference(file_path, 
                                  loadReferenceDepth= "all", 
                                  mergeNamespacesOnClash=False, 
                                  namespace=namespace)

    def _create_texture_node(self, file_path):
        
        # create a file texture read node
        x = cmds.shadingNode('file', asTexture=True)
        cmds.setAttr( "%s.fileTextureName" % x, file_path, type="string" )
        
