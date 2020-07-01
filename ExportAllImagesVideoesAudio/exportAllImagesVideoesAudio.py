# File: exportAllImagesVideoesAudio.py
# Version 1.3
# Date 08:00 18.03.2020
# Copyright (c) 2020 S. A. Ditlefsen
# License: https://opensource.org/licenses/GPL-3.0 GNU General Public License version 3
#
# The following ingest modules have to run in order to get this module to work:
# - File Type Identification
# - Extension Mismatch Detector
# - Embedded File Extractor
# - PhotoRec Carver
# - Virtual Machine Extractor


from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.coreutils import PlatformUtil
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils

import os
from java.io import File
from java.util.logging import Level
import inspect

# Copy Multimedia Factory ---------------------------------------------------------------------------------------------------
class ExportAllImagesVideoesAudioFactory(IngestModuleFactoryAdapter):

    moduleName = "Export All Images Videoes and Audio"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Find all images videoes and audio and exports it to new directory"

    def getModuleVersionNumber(self):
        return "1.3"

    # Return true if module wants to get called for each file
    def isFileIngestModuleFactory(self):
        return True

    # can return null if isFileIngestModuleFactory returns false
    def createFileIngestModule(self, ingestOptions):
        return ExportAllImagesVideoesAudio()

# Copy Multimedia ----------------------------------------------------------------------------------------------------------
class ExportAllImagesVideoesAudio(FileIngestModule):

    _logger = Logger.getLogger(ExportAllImagesVideoesAudioFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    # Startup
    def startUp(self, context):
        self.filesFound = 0

        # List of images and videoes
        self.listOfMimeToCopy = ['image/bmp','image/gif', 'image/heic', 'image/jpeg', 'image/png', 'image/tiff',
                                'image/vnd.adobe.photoshop', 'image/x-raw-nikon', 'image/x-ms-bmp', 'image/x-icon', 'image/webp',
                                'image/vnd.microsoft.icon', 'image/x-rgb', 'image/x-ms-bmp','image/x-xbitmap','image/x-portable-graymap',
                                'image/x-portable-bitmap', 
                                'video/webm', 'video/3gpp', 'video/3gpp2', 'video/ogg','video/mpeg', 
                                'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-flv', 'video/x-m4v', 
                                'video/x-ms-wmv', 
                                'audio/midi', 'audio/mpeg', 'audio/webm', 'audio/ogg', 'audio/wav', 
                                'audio/vnd.wave', 'audio/x-ms-wma']

        # Export directory (C:\Users\user\Documents\cases\1568795\Autopsy\1568795_2020_5060_90_1_sofias_pc\Export)
        exportDirectory = Case.getCurrentCase().getExportDirectory()
        caseName = Case.getCurrentCase().getName()
        number = Case.getCurrentCase().getNumber()

	# Export make C:\Users\user\Documents\cases\1568795\
        exportDirectory = exportDirectory.replace("\\Autopsy", "");
        exportDirectory = exportDirectory.replace("\\" + str(number), "");
        exportDirectory = exportDirectory.replace("\\Export", "");
        self.log(Level.INFO, "==> 1) exportDirectory=" + str(exportDirectory) + " number=" + str(number) + " caseName=" + str(caseName))
        try: 
                os.mkdir(exportDirectory)
        except:
                pass

	# Export make C:\Users\user\Documents\cases\1568795\Img_video_audio
        exportDirectory = os.path.join(exportDirectory, "Img_video_audio")
        self.log(Level.INFO, "==> 2) exportDirectory=" + str(exportDirectory) + " number=" + str(number))
        try: 
                os.mkdir(exportDirectory)
        except:
                pass

	# Export make C:\Users\user\Documents\cases\1568795\Img_video_audio\1568795_2020_5060_90_1_sofias_pc
        exportDirectory = os.path.join(exportDirectory, number)
        self.log(Level.INFO, "==> 3) exportDirectory=" + str(exportDirectory) + " number=" + str(number))
        try: 
                os.mkdir(exportDirectory)
        except:
                pass


	# Pass parameter
	self.exportDirectoryGlobal = exportDirectory;

        pass


    # Process
    def process(self, file):
        # Skip non-files
        if ((file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNALLOC_BLOCKS) or
            (file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNUSED_BLOCKS) or
            (file.isFile() == False)):
            return IngestModule.ProcessResult.OK

        # Blackboard
        blackboard = Case.getCurrentCase().getServices().getBlackboard()




        # For an example, we will flag files with .txt in the name and make a blackboard artifact.
        if(file.getMIMEType() in self.listOfMimeToCopy):

                # Recreate path
                uniquePathFullLinux = file.getUniquePath();
                
                # Recreate path Windows
                uniquePathFullWindows = uniquePathFullLinux.replace("/", "\\")
                uniquePathFullWindows = uniquePathFullWindows[1:]
                
                fileName = os.path.basename(uniquePathFullWindows)
                uniquePathWindows = uniquePathFullWindows.replace(fileName, "");
		
		# uniquePathWindows = img_1568795_2020_5060_90_1_sofias_pc.001\vol_vol3\ProgramData\Microsoft\Windows\SystemData\S-1-5-21-1960575443-3642755368-4161086620-1001\ReadOnly\LockScreen_W\
		# Remove "img_1568795_2020_5060_90_1_sofias_pc.001\"
                # self.log(Level.INFO, "==> 4) uniquePathWindows=" + str(uniquePathWindows))
		replaceImgName = "img_" + str(Case.getCurrentCase().getNumber()) + ".001\\"
                uniquePathWindows = uniquePathWindows.replace(replaceImgName, "");
		

                # Create directory
                splitDir = uniquePathWindows.split("\\")
                pathToCreate = os.path.join(self.exportDirectoryGlobal, "")
                for directory in splitDir:
                        directory = directory.replace(":", "")
                        pathToCreate = os.path.join(pathToCreate, directory)
                        # self.log(Level.INFO, "==> directory=" + str(directory) + " pathToCreate=" + str(pathToCreate))

                        try: 
                                os.mkdir(pathToCreate)
                        except:
                                pass

                # Write file
                try:
                        extractedFile = os.path.join(pathToCreate, file.getName())
                        ContentUtils.writeToFile(file, File(extractedFile))
                except:
                        self.log(Level.SEVERE, "Error writing File " + file.getName() + " to " + extractedFile)

                # Make artifact on blackboard
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT)
                att = BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SET_NAME, ExportAllImagesVideoesAudioFactory.moduleName, "Images, videoes and audio")
                art.addAttribute(att)

                # Index artifact
                try:
                        # index the artifact for keyword search
                        blackboard.indexArtifact(art)
                except Blackboard.BlackboardException as e:
                        self.log(Level.SEVERE, "Error indexing artifact " + art.getDisplayName())

                # UI
                IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent(ExportAllImagesVideoesAudioFactory.moduleName, BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT, None))

        return IngestModule.ProcessResult.OK

    # Shutdown
    def shutDown(self):
        # As a final part of this example, we'll send a message to the ingest inbox with the number of files found (in this thread)
        message = IngestMessage.createMessage(
            IngestMessage.MessageType.DATA, ExportAllImagesVideoesAudioFactory.moduleName,
                str(self.filesFound) + " files found")
        ingestServices = IngestServices.getInstance().postMessage(message)
