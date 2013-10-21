# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from P4 import P4

def get_connection():
    """
    
    """
    p4 = P4()
    
    p4.port = "Alans-Macbook-Pro.local:1668"
    p4.user = "Alan"
    #p4.password = "spiders"
    
    p4.connect()
    return p4
    