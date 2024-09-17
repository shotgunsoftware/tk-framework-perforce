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
from itertools import chain

# import photoshop

import sgtk
from sgtk import Hook
from sgtk import TankError

TK_FRAMEWORK_PERFORCE_NAME = "tk-framework-perforce_v0.x.x"


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
        results = []
        adobe = self.parent.engine.adobe

        doc = adobe.app.activeDocument

        p4_fw = self.load_framework(TK_FRAMEWORK_PERFORCE_NAME)
        p4 = p4_fw.connection.connect()

        # validate tasks:
        for task in tasks:
            item = task["item"]
            output = task["output"]
            errors = []

            # report progress:
            progress_cb(0, "Validating", task)

            # pre-publish item here, e.g.
            if output["name"] == "p4_submit":
                # this is always valid!
                pass
            elif output["name"] == "export_layers":
                # check that the specified layer is still valid:
                layer_errors = self.__validate_layer(doc, item["name"], work_template, output["publish_template"], p4, p4_fw)
                if layer_errors:
                    errors += layer_errors

            elif output["name"] == "send_to_review":
                # this is always valid!
                pass
            else:
                errors.append("Don't know how to publish this item!")

            # if there is anything to report then add to result
            if len(errors) > 0:
                # add result:
                results.append({"task": task, "errors": errors})

            progress_cb(100)

        return results

    def __validate_layer(self, doc, layer_name, work_template, publish_template, p4, p4_fw):
        """
        Validate the specified layer:
        """
        errors = []

        scene_file = doc.fullName.nativePath
        layer = doc.artLayers.getByName(layer_name)

        # check layer actually exists!
        if not layer:
            errors.append("Layer '%s' could not be found!" % layer_name)

        # work out the export path for the layer:
        layer_short_name = {"diffuse": "c", "normal": "n", "specular": "s"}.get(layer_name)
        export_path = None
        try:
            fields = work_template.get_fields(scene_file)
            fields = dict(chain(fields.items(), self.parent.context.as_template_fields(publish_template).items()))
            fields["TankType"] = "%s Texture" % layer_name.capitalize()
            fields["layer_short_name"] = layer_short_name

            export_path = publish_template.apply_fields(fields).encode("utf8")
        except TankError, e:
            errors.append("Failed to construct export path for layer '%s': %s" % (layer_name, e))

        if export_path:
            # check that the file can be opened for edit in Perforce:
            try:
                p4_fw.util.open_file_for_edit(p4, export_path, test_only=True)
            except TankError, e:
                errors.append("%s" % e)

        return errors
