# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

def log_warnings_and_errors(fw, p4):
    """
    Call this to report all errors and warnings for the
    most recent perforce command that was run
    """
    for error in p4.errors:
        fw.log_error("[Perforce]: %s" % error)
    for warning in p4.warnings:
        fw.log_warning("[Perforce]: %s" % warning)