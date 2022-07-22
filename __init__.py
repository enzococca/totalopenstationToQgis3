# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Totalopenstation
                                 A QGIS plugin
 Total Open Station (TOPS for friends) is a free software program for downloading and processing data from total station devices.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-01
        copyright            : (C) 2021 by Enzo Cocca adArte srl; Stefano Costa
        email                : enzo.ccc@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
import os

import re

from qgis.core import QgsMessageLog, Qgis, QgsSettings
L=QgsSettings().value("locale/userLocale")[0:2]
missing_libraries = []
try:
    

    import totalopenstation

    

except Exception as e:
    missing_libraries.append(str(e))
try:
    

    import serial

    

except Exception as e:
    missing_libraries.append(str(e))
try:
    

    import serial.tools

    

except Exception as e:
    missing_libraries.append(str(e))


install_libraries = []
for l in missing_libraries:
    p = re.findall(r"'(.*?)'", l)
    install_libraries.append(p[0])

install_libraries = []
for l in missing_libraries:
    p = re.findall(r"'(.*?)'", l)
    install_libraries.append(p[0])

if install_libraries:
    '''legge le librerie mancanti dalla cartella ext-libs'''
    import site
    site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/ext-libs'))

def classFactory(iface):  # pylint: disable=invalid-name
    """Load Totalopenstation class from file Totalopenstation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    
    from .totalstation import Totalopenstation
    return Totalopenstation(iface)
