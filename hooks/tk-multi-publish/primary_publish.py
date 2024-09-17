# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk import Hook
from sgtk import TankError

import os

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"


class PrimaryPublishHook(Hook):
    """
    Single hook that implements publish of the primary task
    """

    def execute(self, task, work_template, comment, thumbnail_path, sg_task, progress_cb, **kwargs):
        """
        Main hook entry point
        :param task:            Primary task to be published.  This is a
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

        :param comment:         String
                                The comment provided for the publish

        :param thumbnail:       Path string
                                The default thumbnail provided for the publish

        :param sg_task:         Dictionary (shotgun entity description)
                                The shotgun task to use for the publish

        :param progress_cb:     Function
                                A progress callback to log progress during pre-publish.  Call:

                                    progress_cb(percentage, msg)

                                to report progress to the UI

        :returns:               Path String
                                Hook should return the path of the primary publish so that it
                                can be passed as a dependency to all secondary publishes

        :raises:                Hook should raise a TankError if publish of the
                                primary task fails
        """
        # get the engine name from the parent object (app/engine/etc.)
        engine_name = self.parent.engine.name

        # load the perforce framework:
        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)

        # create a publisher instance depending on the engine:
        publisher = None
        if engine_name == "tk-3dsmax":
            publisher = MaxPublisher(self.parent, p4_fw)
        if engine_name == "tk-3dsmaxplus":
            publisher = MaxPlusPublisher(self.parent, p4_fw)
        if engine_name == "tk-maya":
            publisher = MayaPublisher(self.parent, p4_fw)
        elif engine_name == "tk-photoshop":
            publisher = PhotoshopPublisher(self.parent, p4_fw)
        elif engine_name == "tk-photoshopcc":
            publisher = PhotoshopCCPublisher(self.parent, p4_fw)

        if publisher:
            return publisher.do_publish(task, work_template, comment, thumbnail_path, sg_task, progress_cb)
        else:
            raise TankError("Unable to perform publish for unhandled engine %s" % engine_name)


class PublisherBase(object):
    """
    Publisher base class - implements the main publish functionality with
    virtual methods provided to be overwridden in derived, application
    specific classes.
    """

    def __init__(self, bundle, p4_fw):
        """
        Construction
        """
        self.parent = bundle
        self.p4_fw = p4_fw

    def do_publish(self, task, work_template, comment, thumbnail_path, sg_task, progress_cb):
        """
        Publish the scene into Perforce and register the Publish data ready
        for the Perforce hook to pick it up when syncing with Shotgun
        """
        # get the scene path:
        scene_path = self._get_scene_path()

        if not work_template.validate(scene_path):
            raise TankError("File '%s' is not a valid work path, unable to publish!" % scene_path)

        # find scene dependencies
        progress_cb(0.0, "Finding scene dependencies", task)
        dependencies = self._find_scene_dependencies()

        # open a Perforce connection:
        progress_cb(5.0, "Connecting to Perforce...")
        p4 = self.p4_fw.connection.connect()

        # Ensure the file is checked out/added to depot:
        progress_cb(10.0, "Ensuring file is checked out...")
        self.p4_fw.util.open_file_for_edit(p4, scene_path)

        # save the scene using the save_scene_fn passed in:
        progress_cb(30.0, "Saving the scene")
        self.parent.log_debug("Saving the scene...")
        self._save()

        # now, because this is the primary publish, we can create a new
        # changelist for all files being published:
        progress_cb(50.0, "Creating new Perforce changelist...")
        new_change = self.p4_fw.util.create_change(p4, comment or "Shotgun publish")

        # store the change on the primary item 'other_params' so that it can be
        # found by the following secondary publish hook:
        task["item"].setdefault("other_params", dict())["p4_change"] = new_change

        # and add the file to this change:
        progress_cb(60.0, "Adding scene file to change...")
        self.p4_fw.util.add_to_change(p4, new_change, scene_path)

        # next, we want to save the publish metadata so that the sync daemon
        # can pick it up and add to the publish record:
        progress_cb(70.0, "Storing publish data...")
        publish_data = {"thumbnail_path": thumbnail_path,
                        "dependency_paths": dependencies,
                        "task": sg_task,
                        "comment": comment,
                        "context": self.parent.context,
                        "published_file_type": task["output"]["tank_type"],
                        "created_by": self.parent.context.user
                        }
        self.p4_fw.store_publish_data(scene_path, publish_data)

        progress_cb(100)

        return scene_path

    def _get_scene_path(self):
        """
        Return the current scene path
        """
        raise NotImplementedError()

    def _save(self):
        """
        Save the current scene
        """
        raise NotImplementedError()

    def _find_scene_dependencies(self):
        """
        Find dependencies for the current scene
        """
        return []


class MaxPublisher(PublisherBase):
    """
    3ds Max specific instance of the Publisher class
    """

    def _get_scene_path(self):
        """
        Return the current scene path for 3ds Max 
        """
        from Py3dsMax import mxs
        return os.path.abspath(os.path.join(mxs.maxFilePath, mxs.maxFileName))

    def _save(self):
        """
        Save the current scene
        """
        from Py3dsMax import mxs
        scene_path = os.path.abspath(os.path.join(mxs.maxFilePath, mxs.maxFileName))
        mxs.saveMaxFile(scene_path)


class MaxPlusPublisher(PublisherBase):
    """
    3ds Max with MaxPlus specific instance of the Publisher class
    """

    def _get_scene_path(self):
        """
        Return the current scene path for 3ds Max
        """
        import MaxPlus
        return MaxPlus.FileManager.GetFileNameAndPath()

    def _save(self):
        """
        Save the current scene
        """
        import MaxPlus
        scene_path = MaxPlus.FileManager.GetFileNameAndPath()
        MaxPlus.FileManager.Save(scene_path)


class MayaPublisher(PublisherBase):
    """
    Maya specific instance of the Publisher class
    """

    def _get_scene_path(self):
        """
        Return the current scene path for Maya
        """
        import maya.cmds as cmds
        return os.path.abspath(cmds.file(query=True, sn=True))

    def _save(self):
        """
        Save the current scene
        """
        import maya.cmds as cmds
        cmds.file(save=True, force=True)

    def _find_scene_dependencies(self):
        """
        Find dependencies for the current scene
        """
        import maya.cmds as cmds

        # default implementation looks for references and
        # textures (file nodes) and returns any paths that
        # match a template defined in the configuration
        ref_paths = set()

        # first let's look at maya references
        ref_nodes = cmds.ls(references=True)
        for ref_node in ref_nodes:
            # get the path:
            ref_path = cmds.referenceQuery(ref_node, filename=True)
            # make it platform dependent
            # (maya uses C:/style/paths)
            ref_path = ref_path.replace("/", os.path.sep)
            if ref_path:
                ref_paths.add(ref_path)

        # now look at file texture nodes
        for file_node in cmds.ls(l=True, type="file"):
            # ensure this is actually part of this scene and not referenced
            if cmds.referenceQuery(file_node, isNodeReferenced=True):
                # this is embedded in another reference, so don't include it in the
                # breakdown
                continue

            # get path and make it platform dependent
            # (maya uses C:/style/paths)
            texture_path = cmds.getAttr("%s.fileTextureName" % file_node).replace("/", os.path.sep)
            if texture_path:
                ref_paths.add(texture_path)

        # now, for each reference found, build a list of the ones
        # that resolve against a template:
        dependency_paths = []
        for ref_path in ref_paths:
            # see if there is a template that is valid for this path:
            for template in self.parent.sgtk.templates.values():
                if template.validate(ref_path):
                    dependency_paths.append(ref_path)
                    break

        return dependency_paths


class PhotoshopPublisher(PublisherBase):
    """
    Photoshop specific instance of the Publisher class
    """

    def _get_scene_path(self):
        """
        Return the current scene/document path for Photoshop
        """
        import photoshop

        doc = photoshop.app.activeDocument
        if not doc:
            raise TankError("There is no currently active document!")

        # get scene path
        return doc.fullName.nativePath

    def _save(self):
        """
        Save the current scene
        """
        import photoshop

        doc = photoshop.app.activeDocument
        if not doc:
            raise TankError("There is no currently active document!")

        doc.save()


class PhotoshopCCPublisher(PublisherBase):
    """
    Photoshop specific instance of the Publisher class
    """

    def _get_scene_path(self):
        """
        Return the current scene/document path for Photoshop
        """
        adobe = self.parent.engine.adobe

        try:
            doc = adobe.app.activeDocument
        except RuntimeError:
            raise TankError("There is no active document!")

        try:
            scene_path = doc.fullName.fsName
        except RuntimeError:
            raise TankError("Please save your file before publishing!")

        return scene_path

    def _save(self):
        """
        Save the current scene
        """
        adobe = self.parent.engine.adobe

        try:
            doc = adobe.app.activeDocument
        except RuntimeError:
            raise TankError("There is no active document!")

        doc.save()
