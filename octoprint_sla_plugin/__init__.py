
#!/usr/bin/python
# coding=utf-8


import os


from .chitu_comm import chitu_comm
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
    #                  Settings                  #
    ##############################################

    def get_settings_defaults(self):
        return dict(
            
            allowedExten = 'cbddlp, photon',
            workAsFlashDrive = True, #false printer use separate flash drive
            flashDriveImageSize = 1,#GB
            chitu_comm = True,
            hideTempTab = True,
            #hideControlTab = True,
            hideGCodeTab = True,
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
            tempSensorBed = None,#1wire/ntc

            helloCommand = "M4002"
            #M27 (status)
            #M4002 (version)

            #dynamicLedFanControl =
            #  

        )

    def rewrite_test(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        print(gcode)
        #if gcode and gcode == "M107":
            #cmd = "M106 S0"
        return #cmd,
    
    def get_template_configs(self):
        return [

                dict(type="tab", name="Sla-control", replaces="control" , div="control" ,template="sla_plugin_tab.jinja2" , custom_bindings=False),
                dict(type="tab", name="Modelview", template="Modeleditor.jinja2" , custom_bindings=False)
        ]
    


    ##############################################
    #                UDP Upload                  #
    ##############################################

    def on_after_startup(self):
        
        if self._settings.get(["chitu_comm"]):

            self.Chitu_comm = chitu_comm(self)
            self.Chitu_comm.start_listen_reqest()
            self._logger.info("chitubox udp reciver enabeled")

        

        self.hideTempTab = self._settings.get_boolean(["hideTempTab"])
        self.hideControlTab = self._settings.get_boolean(["hideControlTab"])
        self.hideGCodeTab = self._settings.get_boolean(["hideGCodeTab"])

        setTabs(self)

        self._settings.global_set(["serial", "helloCommand"], self._settings.get(["helloCommand"]))
        self._settings.global_set(["serial", "disconnectOnErrors"], False)
        #self._settings.global_set(["serial", "sdAlwaysAvailable"], False)
        #self._settings.global_set(["serial", "firmwareDetection"], False)
        #self._settings.global_set(["serial", "baudrate"], 115200)
        #self._settings.global_set(["serial", "exclusive"], False)
        #"feature""sdSupport"
        #"feature""printStartConfirmation"
        #"feature""pollWatched"
        #"folder""uploads"
        #"folder""watched"




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
    #               gcode modifier               #
    ##############################################


    #print("#########################################")


__plugin_name__ = "Sla_plugin"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = Sla_plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.gcode_modifier.get_gcode_queuing_modifier,
        "octoprint.filemanager.extension_tree"  : __plugin_implementation__.get_extension_tree,
        "octoprint.filemanager.analysis.factory": __plugin_implementation__.get_sla_analysis_factory,
        "octoprint.printer.factory"             : __plugin_implementation__.get_sla_printer_factory,
        "octoprint.comm.protocol.gcode.sending" : __plugin_implementation__.gcode_modifier.get_gcode_send_modifier,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.gcode_modifier.get_gcode_receive_modifier

        #"octoprint.comm.protocol.gcode.error": handle_error
    }

