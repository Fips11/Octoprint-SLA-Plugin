
#!/usr/bin/python
# coding=utf-8


import os
import logging

from .chitu_comm import chitu_comm
from .flash_drive_emu import flash_drive_emu
from .sla_analyser import sla_AnalysisQueue
from .sla_printer import Sla_printer, gcode_modifier
from .sla_ui import *

import octoprint.plugin
#import octoprint.util

#from octoprint.settings import settings

import octoprint.filemanager
import octoprint.filemanager.util
from octoprint.filemanager import ContentTypeMapping


class Sla_plugin(   octoprint.plugin.SettingsPlugin,
                    octoprint.plugin.SimpleApiPlugin,
                    octoprint.plugin.AssetPlugin,
                    octoprint.plugin.TemplatePlugin,
                    octoprint.plugin.StartupPlugin,
                    octoprint.plugin.EventHandlerPlugin,
                    octoprint.plugin.ShutdownPlugin
                    ):

    
    #def __init__(self,**kwargs):
    def __init__(self, **kwargs):
        super(Sla_plugin, self).__init__(**kwargs)
    
        self.gcode_modifier = gcode_modifier()


    
    

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
    #              add pi's uart                 #
    ##############################################


    ##############################################
    #                change ui                   #
    ##############################################

    def get_template_configs(self):
        return [

                dict(type="tab", name="Sla-control", replaces="control" , div="control" ,template="sla_plugin_tab.jinja2" , custom_bindings=False),
                dict(type="tab", name="Modelview", template="Modeleditor.jinja2" , custom_bindings=False),
                dict(type="settings", custom_bindings=False)
        ]
    

    
    ##############################################
    #                  Settings                  #
    ##############################################

    def get_settings_defaults(self):
        return dict(
            
            allowedExten = 'cbddlp, photon',
            deaultBaudRate = 115200,
            additionalPorts = "/dev/ttyAMA*",
            workAsFlashDrive = True, #false printer use separate flash drive
            flashFirstRun = True,
            flashDriveImageSize = 1,#GB
            chitu_comm = True,
            hideTempTab = True,
            hideControlTab = False,
            hideGCodeTab = True,
            useHeater = False,
            heaterTemp = 30,# C
            heaterTime = 20,#min
            resinGauge = True,
            enableLight = False, #ir cam light
            #printerInternalConfig = [dict(
                #allGcodeFileEntrys
            #)],
            mainpowerSwitch = None,#net/gpio
            photonFileEditor = False,
            tempSensorPrinter = None,#1wire/ntc
            tempSensorBed = None,#1wire/ntc

            helloCommand = "M4002"
            #M27 (status)
            #M4002 (version)

            #dynamicLedFanControl =
            #  

        )

    def on_after_startup(self):
        
        self.hideTempTab = self._settings.get_boolean(["hideTempTab"])
        self.hideControlTab = self._settings.get_boolean(["hideControlTab"])
        self.hideGCodeTab = self._settings.get_boolean(["hideGCodeTab"])

        setTabs(self)

        self._settings.global_set(["serial", "helloCommand"], self._settings.get(["helloCommand"]))
        self._settings.global_set(["serial", "disconnectOnErrors"], False)
        self._settings.global_set(["serial", "sdAlwaysAvailable"], False)
        self._settings.global_set(["serial", "firmwareDetection"], False)
        self._settings.global_set(["serial", "baudrate"], self._settings.get(["deaultBaudRate"]))
        self._settings.global_set(["serial", "exclusive"], False)

        #add raspberry uart to the avaliable ports
        ports = self._settings.global_get(["serial", "additionalPorts"])
        if "/dev/ttyAMA*" not in ports:
            ports.append("/dev/ttyAMA*")
        self._settings.global_set(["serial", "additionalPorts"], ports)

        #set folder,uploads entry to mounted usb flash image



        #"feature""sdSupport"
        #"feature""printStartConfirmation"
        #"feature""pollWatched"
        #"folder""uploads"
        #"folder""watched"
    ##############################################
    #            USB Flash Feature               #
    ##############################################

        if self.workAsFlashDrive : ## nicht getestet
            try:
                self.flash =  flash_drive_emu( self._settings.get_boolean(["flashFirstRun"]) )
                if self.flash.errorcode = 0:
                    self._settings.set_boolean(["flashFirstRun"], False)

            except Exception as identifier:
                print(identifier)
                self.flash = None




    ##############################################
    #                UDP Upload                  #
    ##############################################

        if self._settings.get(["chitu_comm"]):

            #TODO: check if we can write to watched folder

            self.Chitu_comm = chitu_comm(self)
            self.Chitu_comm.start_listen_reqest()
            self._logger.info("chitubox udp reciver enabeled")


        #more at octoprint/settings.py
    def on_shutdown(self):
        self.Chitu_comm.shutdownService()

    ##############################################
    #               File analysis                #
    ##############################################
    def get_sla_analysis_factory(*args, **kwargs):
        return dict(sla_bin=sla_AnalysisQueue)


    ##############################################
    #               Priterfactory                #
    ##############################################
    
    def get_sla_printer_factory(self,components):

        self.sla_printer = Sla_printer(components["file_manager"],components["analysis_queue"],components["printer_profile_manager"])
        return self.sla_printer

    ##############################################
    #               Plugin Update                #
    ##############################################

    def get_update_information(self):

        return dict(sla_plugin=dict(
            displayName='SLA_Support',
            displayVersion=self._plugin_version,
            type="github_commit",
            user='Fips11',
            repo='Octoprint-SLA-Plugin',
            current=self._plugin_version,
            pip='https://github.com/Fips11/Octoprint-SLA-Plugin/archive/{target_version}.zip'))



__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = Sla_plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.gcode_modifier.get_gcode_queuing_modifier,
        "octoprint.filemanager.extension_tree"  : __plugin_implementation__.get_extension_tree,
        "octoprint.filemanager.analysis.factory": __plugin_implementation__.get_sla_analysis_factory,
        "octoprint.printer.factory"             : __plugin_implementation__.get_sla_printer_factory,
        "octoprint.comm.protocol.gcode.sending" : __plugin_implementation__.gcode_modifier.get_gcode_send_modifier,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.gcode_modifier.get_gcode_receive_modifier

        #"octoprint.comm.protocol.gcode.error": handle_error
    }

