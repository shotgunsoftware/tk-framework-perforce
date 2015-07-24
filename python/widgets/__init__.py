# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtGui
if hasattr(QtGui, "QWidget"):
    from .open_connection_form import OpenConnectionForm
    from .password_form import PasswordForm
    from .select_workspace_form import SelectWorkspaceForm
    from .trust_form import TrustForm