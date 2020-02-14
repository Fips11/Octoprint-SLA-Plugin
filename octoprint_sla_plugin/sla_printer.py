
# coding=utf-8

import os

from octoprint.filemanager import FileDestinations, NoSuchStorage, valid_file_type, full_extension_tree
from octoprint.printer.standard import Printer
from octoprint.util import is_hidden_path, to_unicode, timing

import logging


from octoprint.settings import settings

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
			#Printer.startPrint(self, pos, user, external_sd=True)
			#print(dir(self._comm))
			#print("printjob canceled")

			"""
			Starts the currently loaded print job.
			Only starts if the printer is connected and operational, not currently printing and a printjob is loaded
			"""
			if self._comm is None or not self._comm.isOperational() or self._comm.isPrinting():
				return

			with self._selectedFileMutex:
				if self._selectedFile is None:
					return

			self._fileManager.delete_recovery_data()

			self._lastProgressReport = None
			self._updateProgressData()
			self._setCurrentZ(None)

			self._comm.sendCommand("M6030 '{filename}'".format(filename=self._comm._currentFile.getFilename().split(u"/")[-1]))

			#			                 part_of_job=True,
			#			                 tags=kwargs.get("tags", set()) | {"trigger:printer.start_print"})
 

	def add_sd_file(self, filename, path, on_success=None, on_failure=None, *args, **kwargs):

		self.fileType = self.get_fileType(path)

		if self.fileType == "gcode": 
			ret = Printer.add_sd_file(self, filename, path, on_success, on_failure, *args, **kwargs)


		elif self.fileType == "sla_bin":

			on_success()
			print("printjob canceled")
			

	def get_fileType(self,path):
		tree = full_extension_tree()["machinecode"]

		for key in tree:
			if valid_file_type(path,type=key):
				#self.fileType = key
				return key

		return None

	def split_path(self, path):
		path = to_unicode(path)
		split = path.split(u"/")
		if len(split) == 1:
			return u"", split[0]
		else:
			return self.join_path(*split[:-1]), split[-1]



class gcode_modifier():
	def __init__(self):
		pass

	def get_gcode_receive_modifier(self, comm_instance, line):
		print(line)
		
		if line.startswith('ok V'): # proceed hello command # ok V4.2.20.3_LCDM

			
			return 'ok start' + line

		else:
			return line


	def get_gcode_send_modifier(self, comm_instance, phase, cmd, cmd_type, gcode,subcode=None , tags=None):

		# suppress comments
		if cmd.upper().lstrip().startswith(';') or cmd.upper().lstrip().startswith('('): #suppress comment
			return (None, )

		elif cmd.upper().startswith('M110'): #suppress lienresett
			return (None, )
	
		elif cmd.upper().startswith('M105'):#suppress temppoll
			return (None, )
		
		#elif cmd.upper().startswith('G90'):#suppress temppoll
		#	return (None, )

		#elif cmd.upper().startswith('G91'):#suppress temppoll
		#	return (None, )
		
		else:
			print("#####################################################")
			print(cmd)
			print("#####################################################")
