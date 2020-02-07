#!/usr/bin/python
# -*- coding: utf-8 -*-

from octoprint.filemanager.analysis import AbstractAnalysisQueue
import pprint
import struct
import yaml

class sla_AnalysisQueue(AbstractAnalysisQueue):

        """
        A queue to analyze GCODE files. Analysis results are :class:`dict` instances structured as follows:

        .. list-table::
        :widths: 25 70

        - * **Key**
            * **Description**
        - * ``estimatedPrintTime``
            * Estimated time the file take to print, in seconds

        - * ``filament.volume``
            * The used volume in cm³

        - * ``printingArea``
            * Bounding box of the printed object in the print volume (minimum and maximum coordinates)

        - * ``printingArea.minX``
            * Minimum X coordinate of the printed object
        - * ``printingArea.maxX``
            * Maximum X coordinate of the printed object
        - * ``printingArea.minY``
            * Minimum Y coordinate of the printed object
        - * ``printingArea.maxY``
            * Maximum Y coordinate of the printed object
        - * ``printingArea.minZ``
            * Minimum Z coordinate of the printed object
        - * ``printingArea.maxZ``
            * Maximum Z coordinate of the printed object
        - * ``dimensions``

            * Dimensions of the printed object in X, Y, Z
        - * ``dimensions.width``

            * Width of the printed model along the X axis, in mm
        - * ``dimensions.depth``
            * Depth of the printed model along the Y axis, in mm
        - * ``dimensions.height``
            * Height of the printed model along the Z axis, in mm
        """

        def __init__(self, finished_callback):
            AbstractAnalysisQueue.__init__(self, finished_callback)

            self._aborted = False
            self._reenqueue = False

            #if self._current.analysis:
            #    return self._current.analysis



        def _do_analysis(self, high_priority=False):
            #print("#########################################")
            #print("try analysis")
            #print(self._current)
            #print("#########################################")
            #print(self._current.type)
            #print("#########################################")
            #print(self._current.absolute_path)
            #print("#########################################")
            #print(self._current.printer_profile)
            #print("#########################################")

            blocksize = 81 #filehead

            with open(self._current.absolute_path, "rb") as f:

                buffer = f.read(blocksize)

                f.close()

            result = dict()

            result["header1"] =                       struct.unpack_from('<I', buffer[0:4])[0]

            result["header2"] =                       struct.unpack_from('<I', buffer[4:8])[0]

            result["bedXmm"] =                        round(struct.unpack_from('<f', buffer[8:12])[0], 2)    

            result["bedYmm"] =                        round(struct.unpack_from('<f', buffer[12:16])[0], 2)

            result["bedZmm"] =                        round(struct.unpack_from('<f', buffer[16:20])[0], 2)

            result["unknown1"] =                      struct.unpack_from('<I', buffer[20:24])[0]

            result["unknown2"] =                      struct.unpack_from('<I', buffer[24:28])[0]

            result["unknown3"] =                      struct.unpack_from('<I', buffer[28:32])[0]

            result["layerHeightMilimeter"] =          round(struct.unpack_from('<f', buffer[32:36])[0], 2)

            result["exposureTimeSeconds"] =           round(struct.unpack_from('<f', buffer[36:40])[0], 2)
            result["exposureBottomTimeSeconds"] =     round(struct.unpack_from('<f', buffer[40:44])[0], 2)
            result["offTimeSeconds"] =                round(struct.unpack_from('<f', buffer[44:48])[0], 2)

            result["bottomLayers"] =                  struct.unpack_from('<I', buffer[48:52])[0]

            result["resolutionX"] =                   struct.unpack_from('<I', buffer[52:56])[0]
            result["resolutionY"] =                   struct.unpack_from('<I', buffer[56:60])[0]

            result["previewOneOffsetAddress"] =       struct.unpack_from('<I', buffer[60:64])[0]
            result["layersDefinitionOffsetAddress"] = struct.unpack_from('<I', buffer[64:68])[0]

            result["numberOfLayers"] =                struct.unpack_from('<I', buffer[68:72])[0]

            result["previewTwoOffsetAddress"] =       struct.unpack_from('<I', buffer[72:76])[0]
            result["unknown4"] =                      struct.unpack_from('<I', buffer[76:80])[0]
            
            return result


        def _do_abort(self, reenqueue=True):
		    self._aborted = True
		    self._reenqueue = reenqueue
            