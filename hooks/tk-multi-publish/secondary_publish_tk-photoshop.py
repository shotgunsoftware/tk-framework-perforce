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
import tempfile
import uuid
import re
from itertools import chain

import photoshop

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
        if not primary_change:
            raise TankError("Failed to find the Perforce change in the secondary publish hook!")
        
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
        
            if output["name"] == "export_layers":
                # publish the layer as a tif:
                export_errors = self.__publish_layer_as_tif(item["name"], 
                                                            work_template,
                                                            output["publish_template"],
                                                            primary_publish_path,
                                                            sg_task,
                                                            comment,
                                                            p4,
                                                            p4_fw,
                                                            primary_change,                                                            
                                                            progress_cb)
                if export_errors:
                    errors += export_errors
            elif output["name"] == "send_to_review":
                # register review data for the current document:
                review_errors = self.__send_to_review(primary_publish_path, sg_task, comment, p4, p4_fw, progress_cb)
                if review_errors:
                    errors += review_errors
            else:
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


    def __publish_layer_as_tif(self, layer_name, work_template, publish_template, primary_publish_path, 
                               sg_task, comment, p4, p4_fw, change, progress_cb):
        """
        Publish the specified layer
        """
        errors = []
        MAX_THUMB_SIZE = 512

        # publish type will be driven from the layer name:
        publish_type = "%s Texture" % layer_name.capitalize()

        # generate the export path using the correct template together
        # with the fields extracted from the work template:
        export_path = None
        
        progress_cb(10, "Building output path")
        
        layer_short_name = {"diffuse":"c", "normal":"n", "specular":"s"}.get(layer_name)
        try:
            fields = work_template.get_fields(primary_publish_path)
            fields = dict(chain(fields.items(), self.parent.context.as_template_fields(publish_template).items()))
            fields["TankType"] = publish_type
            fields["layer_short_name"] = layer_short_name            
        
            export_path = publish_template.apply_fields(fields).encode("utf8")
        except TankError, e:
            errors.append("Failed to construct export path for layer '%s': %s" % (layer_name, e))
            return errors

        # ensure the export folder exists:
        export_folder = os.path.dirname(export_path)
        self.parent.ensure_folder_exists(export_folder)

        file_in_perforce = False
        if os.path.exists(export_path):
            # check out the file if it's already in Perforce:
            progress_cb(15, "Checking out file from Perforce")
            try:
                p4_fw.util.open_file_for_edit(p4, export_path)
            except TankError, e:
                errors.append("%s" % e)
                return errors
            file_in_perforce = True

        # get a path in the temp dir to use for the thumbnail:
        thumbnail_path = os.path.join(tempfile.gettempdir(), "%s_sgtk.png" % uuid.uuid4().hex)

        # set unit system to pixels:
        original_ruler_units = photoshop.app.preferences.rulerUnits
        pixel_units = photoshop.StaticObject('com.adobe.photoshop.Units', 'PIXELS')
        photoshop.app.preferences.rulerUnits = pixel_units        

        try:
            active_doc = photoshop.app.activeDocument
            orig_name = active_doc.name
            width_str = active_doc.width
            height_str = active_doc.height
            
            # calculate the thumbnail doc size:
            doc_width = doc_height = 0
            exp = re.compile("^(?P<value>[0-9]+) px$")
            mo = exp.match (width_str)
            if mo:
                doc_width = int(mo.group("value"))
            mo = exp.match (height_str)
            if mo:
                doc_height = int(mo.group("value"))
    
            thumb_width = thumb_height = 0
            if doc_width and doc_height:
                max_sz = max(doc_width, doc_height)
                if max_sz > MAX_THUMB_SIZE:
                    scale = min(float(MAX_THUMB_SIZE)/float(max_sz), 1.0)
                    thumb_width = max(min(int(doc_width * scale), doc_width), 1)
                    thumb_height = max(min(int(doc_height * scale), doc_height), 1)
            
            # set up the export options and get a file object:
            layer_file = photoshop.RemoteObject('flash.filesystem::File', export_path)        
            tiff_save_options = photoshop.RemoteObject('com.adobe.photoshop::TiffSaveOptions')
            tiff_save_options.layers = False
                    
            # set up the thumbnail options and get a file object:
            thumbnail_file = photoshop.RemoteObject('flash.filesystem::File', thumbnail_path)
            png_save_options = photoshop.RemoteObject('com.adobe.photoshop::PNGSaveOptions')
            
            close_save_options = photoshop.flexbase.requestStatic('com.adobe.photoshop.SaveOptions', 'DONOTSAVECHANGES')              
            
            progress_cb(20, "Exporting %s layer" % layer_name)
            
            # duplicate doc
            doc_name, doc_sfx = os.path.splitext(orig_name)
            layer_doc_name = "%s_%s.%s" % (doc_name, layer_name, doc_sfx)            
            layer_doc = active_doc.duplicate(layer_doc_name)
            try:
                # set layer visibility
                layers = layer_doc.artLayers
                for layer in [layers.index(li) for li in xrange(layers.length)]:
                    layer.visible = (layer.name == layer_name)
                
                # flatten
                layer_doc.flatten()
                
                # save:
                layer_doc.saveAs(layer_file, tiff_save_options, True)
                
                progress_cb(60, "Exporting thumbnail")
                
                # resize for thumbnail
                if thumb_width and thumb_height:
                    layer_doc.resizeImage("%d px" % thumb_width, "%d px" % thumb_height)                  
                
                # save again (as thumbnail)
                layer_doc.saveAs(thumbnail_file, png_save_options, True)
                
            finally:
                # close the doc:
                layer_doc.close(close_save_options)

            # add publish file to the change:
            # Note, if it looks like this is taking ages it's probably just because
            # the progress bar hasn't updated between this and storing the publish
            # data, which can take a bit of time
            progress_cb(80, "Adding to Perforce change %s" % change)
            if not file_in_perforce:
                try:
                    p4_fw.util.open_file_for_edit(p4, export_path)
                except TankError, e:
                    errors.append("%s" % e)
                    return errors
    
            p4_fw.util.add_to_change(p4, change, export_path)
        
            # store additional metadata for the publish:
            progress_cb(85, "Storing publish data")
            publish_data = {"thumbnail_path":thumbnail_path,
                            "dependency_paths":[primary_publish_path],
                            "task":sg_task,
                            "comment":comment,
                            "context":self.parent.context,
                            "published_file_type":publish_type
                            }
            
            try:
                p4_fw.store_publish_data(export_path, publish_data)
            except TankError, e:
                errors.append("Failed to store publish data: %s" % e)            
                
        finally:
            # delete the thumbnail file:
            if os.path.exists(thumbnail_path):
                try:
                    os.remove(thumbnail_path)
                except:
                    pass
            
            # set units back to original
            photoshop.app.preferences.rulerUnits = original_ruler_units

        return errors

    def __send_to_review(self, primary_publish_path, sg_task, comment, p4, p4_fw, progress_cb):
        """
        Create a version of the current document that can be uploaded as a
        Shotgun 'Version' entity and reviewed in Screening Room, etc. 
        """
        errors = []
        
        progress_cb(10, "Saving JPEG version of file")
        
        # set up the export options and get a file object:
        jpeg_path = os.path.join(tempfile.gettempdir(), "%s_sgtk.jpg" % uuid.uuid4().hex)
        jpeg_file = photoshop.RemoteObject('flash.filesystem::File', jpeg_path)
        jpeg_save_options = photoshop.RemoteObject('com.adobe.photoshop::JPEGSaveOptions')
        jpeg_save_options.quality = 12
        
        try:
       
            # save as a copy:
            photoshop.app.activeDocument.saveAs(jpeg_file, jpeg_save_options, True)        
            
            # construct the data needed to create a Shotgun 'Version' entity:
            ctx = self.parent.context
            data = {
                "code":os.path.basename(primary_publish_path),
                "sg_first_frame": 1,
                "frame_count": 1,
                "frame_range": "1-1",
                "sg_last_frame": 1,
                "entity": ctx.entity,
                "sg_path_to_frames": primary_publish_path,
                "project": ctx.project,
                "sg_task": sg_task,
                "sg_uploaded_movie": jpeg_path
            }        
    
            # and store the version data for the publish path:        
            progress_cb(50.0, "Storing review data...")
            try:
                p4_fw.store_publish_review_data(primary_publish_path, data)
            except TankError, e:
                errors.append("Failed to store review data: %s" % e)

        finally:
            # delete the temp jpeg file:
            if os.path.exists(jpeg_path):
                try:
                    os.remove(jpeg_path)
                except:
                    pass
        
        return errors


