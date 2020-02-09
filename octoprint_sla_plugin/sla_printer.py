
# coding=utf-8

import os
#from .helper import *
from octoprint.filemanager import FileDestinations, NoSuchStorage, valid_file_type, full_extension_tree
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
(kann flash image nicht gleich uploadverzeichnis sein? )

-filehandling als sd operationen händeln
-normaler druck als druck von sd karte händeln


infos:
-webinterface sd upload aktion Location: http://192.168.178.67/api/files/sdcard/cfffp_~1.gco
	-läd datei hoch und löst automatisch upload zur sdkarte aus
	- autoprint deaktivieren

	octoprint\printer\standard.py:
		plugin_manager().get_hooks("octoprint.printer.sdcardupload")

	octoprint\server\api\files.py: (line 226)
		@api.route("/files/<string:target>", methods=["POST"]) #händelt sd upload,select und startet stream und print 




Szenario 1 : pi als flashdrive:

uploadverzeichnis = gemountetes image / uploaddir getrennt vom image 
normale serielle kommunikation

Szenario 2 : pi nur über uart verbunden separates flshdrive am drucker:

-anpassung des uploadprozesses für bin files
-kein streamen u drucken wärend des uploads




"""


class Sla_printer(Printer):

	def __init__(self, fileManager, analysisQueue, printerProfileManager):

		self._analysisQueue = analysisQueue
		self._fileManager = fileManager
		self._printerProfileManager = printerProfileManager

		self.fileType = None
		Printer.__init__(self, fileManager, analysisQueue, printerProfileManager)

	def select_file(self, path, sd, printAfterSelect=False, user=None, pos=None, *args, **kwargs):

		self.fileType = self.get_fileType(path)

		Printer.select_file(self, path, sd, printAfterSelect, user, pos)

	def start_print(self, pos=None, user=None, *args, **kwargs):

		if self.fileType == "gcode": 
			Printer.start_print(self, pos, user)
		
		elif self.fileType == "sla_bin":
			print("printjob canceled")


	def add_sd_file(self, filename, path, on_success=None, on_failure=None, *args, **kwargs):

		self.fileType = self.get_fileType(path)

		if self.fileType == "gcode": 
			ret = Printer.add_sd_file(self, filename, path, on_success, on_failure, *args, **kwargs)


		elif self.fileType == "sla_bin":
			print("printjob canceled")
			

	def get_fileType(self,path):
		tree = full_extension_tree()["machinecode"]

		for key in tree:
			if valid_file_type(path,type=key):
				#self.fileType = key
				return key

		return None