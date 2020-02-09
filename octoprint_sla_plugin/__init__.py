
#!/usr/bin/python
# coding=utf-8

#from __future__ import absolute_import
#from octoprint.events import Events

# import sys
#import time
#import math
import os
#import subprocess

from .chitu_comm import chitu_comm
from .sla_analyser import sla_AnalysisQueue
from .sla_printer import Sla_printer


import octoprint.plugin
#import octoprint.util

import octoprint.filemanager
import octoprint.filemanager.util
from octoprint.filemanager import ContentTypeMapping
#from octoprint.filemanager.analysis import AbstractAnalysisQueue


#import re
#import logging
#import json
#import flask


### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.


#from socket import *
#from uuid import getnode as get_mac

class Sla_plugin(   octoprint.plugin.SettingsPlugin,
                    octoprint.plugin.SimpleApiPlugin,
                    octoprint.plugin.AssetPlugin,
                    octoprint.plugin.TemplatePlugin,
                    octoprint.plugin.StartupPlugin,
                    octoprint.plugin.EventHandlerPlugin):


    ##############################################
    #        allowed file extesions part         #
    ##############################################

    @property
    def allowed(self):
        if self._settings is None:
            return str("cbddlp, photon")
        else:
            #self._logger.info("add Extensions: %s " % self._settings.get(["allowedExten"]))
            return str(self._settings.get(["allowedExten"]))


    def get_extension_tree(self, *args, **kwargs):
        return dict(machinecode=dict(sla_bin=ContentTypeMapping(self.allowed.replace(" ", "").split(","), "application/octet-stream")))
 
    ##############################################
    #                  Settings                  #
    ##############################################

    def get_template_configs(self):
		return [dict(type="settings", custom_bindings=False)]

    def get_settings_defaults(self):
        return dict(
            
            allowedExten = 'cbddlp, photon',
            workAsFlashDrive = True, #false printer use separate flash drive
            flashDriveImageSize = 1,#GB
            chitu_comm = True,

            useHeater = False,
            heaterTemp = 30,# C
            heaterTime = 20,#min
            resinGauge = True,
            enableLight = False, #ir cam light
            printerInternalConfig = [dict(
                #allGcodeFileEntrys
            )],
            mainpowerSwitch = None,#net/gpio
            photonFileEditor = False,
            tempSensorPrinter = None,#1wire/ntc
            tempSensorBed = None#1wire/ntc

            #dynamicLedFanControl =
            #  

        )

    ##############################################
    #                UDP Upload                  #
    ##############################################

    def on_after_startup(self):
        
        if self._settings.get(["chitu_comm"]):

            Chitu_comm = chitu_comm(self)
            Chitu_comm.start_listen_reqest()
            self._logger.info("chitubox udp reciver enabeled")

    ##############################################
    #               File analysis                #
    ##############################################
    def get_sla_analysis_factory(*args, **kwargs):
        return dict(sla_bin=sla_AnalysisQueue)


    ##############################################
    #               Priterfactory                #
    ##############################################
    
    def get_sla_printer_factory(self,components):
        return Sla_printer(components["file_manager"],components["analysis_queue"],components["printer_profile_manager"])
    

    ##############################################
    #               gcode modifier               #
    ##############################################
    #reicht nicht. printablauf zu unterschiedlich
"""
    def get_gcode_receive_modifier(self):
        pass

    def get_gcode_send_modifier(self):
        pass
""" 


    #print("#########################################")


__plugin_name__ = "Sla_plugin"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = Sla_plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		
        "octoprint.filemanager.extension_tree"  : __plugin_implementation__.get_extension_tree,
        "octoprint.filemanager.analysis.factory": __plugin_implementation__.get_sla_analysis_factory,
        "octoprint.printer.factory"             : __plugin_implementation__.get_sla_printer_factory
        #'octoprint.comm.protocol.gcode.sending': __plugin_implementation__.get_gcode_send_modifier,
        #'octoprint.comm.protocol.gcode.received': __plugin_implementation__.get_gcode_receive_modifier
    }

"""
fuer neue druckercommandos 

         ----siehe Bettergrblsupport plugin 

kommunikation ueber udp oder serial:

- bei serial alten standartdrucker verwenden und nur gcode hooks nutzen
- fuer udp octoprint/util/comm anpassen

"""
