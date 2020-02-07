
# coding=utf-8

import os
from octoprint.filemanager import FileDestinations, NoSuchStorage, valid_file_type
from octoprint.printer.standard import Printer
#################################################################################################
#                                   Sla printer class                                           #
#################################################################################################


"""
TODO:
-bin to sd upload ermöglichen
-versuche sd upload zu nutzen
-normales drucken blockieren

-sd upload fileübertragung karpern und nach settings entscheiden ob serial upload /udp upload oder verschieben in flashimage
-filehandling als sd operationen händeln
-normaler druck als druck von sd karte händeln


infos:
-webinterface sd upload aktion Location: http://192.168.178.67/api/files/sdcard/cfffp_~1.gco
	-läd datei hoch und löst automatisch upload zur sdkarte aus
	- autoprint deaktivieren

	octoprint\printer\standard.py:
		plugin_manager().get_hooks("octoprint.printer.sdcardupload")

	octoprint\server\api\files.py:
		@api.route("/files/<string:target>", methods=["POST"]) #händelt sd upload,select und startet stream und print


"""


class Sla_printer(Printer):

	def __init__(self, fileManager, analysisQueue, printerProfileManager):

		self._analysisQueue = analysisQueue
		self._fileManager = fileManager
		self._printerProfileManager = printerProfileManager

		self.isGcodeFile = False
		Printer.__init__(self, fileManager, analysisQueue, printerProfileManager)

	def select_file(self, path, sd, printAfterSelect=False, user=None, pos=None, *args, **kwargs):

		#valid_file_type()
		#get_file_type()
		
		if valid_file_type(path,type="sla_bin"):
			self.isGcodeFile = False
		else:
			self.isGcodeFile = True


		Printer.select_file(self, path, sd, printAfterSelect, user, pos)

	def start_print(self, pos=None, user=None, *args, **kwargs):

		if self.isGcodeFile: 
			Printer.start_print(self, pos, user)
		else:
			print("printjob canceled")