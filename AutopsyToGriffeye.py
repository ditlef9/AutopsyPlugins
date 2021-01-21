# File: autopsyToGriffeyeXML.py
# Version 1.0
# Date 13:26 21.01.2021
# Copyright (c) 2021 S. A. Ditlefsen
# License: https://opensource.org/licenses/GPL-3.0 GNU General Public License version 3
#
# About:
# This is a file-level ingest module that export all images and videoes from a 
# image file. It exports all to a folder, and creates two XML files, one with 
# images, one with videoes. The XML files can then be imported intro Griffeye.
#
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
class AutopsyToGriffeyeFactory(IngestModuleFactoryAdapter):

    moduleName = "AutopsyToGriffeye"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "AutopsyToGriffeye"

    def getModuleVersionNumber(self):
        return "1.4"

    # Return true if module wants to get called for each file
    def isFileIngestModuleFactory(self):
        return True

    # can return null if isFileIngestModuleFactory returns false
    def createFileIngestModule(self, ingestOptions):
        return AutopsyToGriffeye()

# Copy Multimedia ----------------------------------------------------------------------------------------------------------
class AutopsyToGriffeye(FileIngestModule):

    _logger = Logger.getLogger(AutopsyToGriffeyeFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    # Startup
    def startUp(self, context):
        self.filesFound = 0

        # List of images and videoes
        self.listOfImagesMimeToCopy = ['image/bmp','image/gif', 'image/heic', 'image/jpeg', 'image/png', 'image/tiff',
                                'image/vnd.adobe.photoshop', 'image/x-raw-nikon', 'image/x-ms-bmp', 'image/x-icon', 'image/webp',
                                'image/vnd.microsoft.icon', 'image/x-rgb', 'image/x-ms-bmp','image/x-xbitmap','image/x-portable-graymap',
                                'image/x-portable-bitmap', ]

        self.listOfVideosMimeToCopy = ['video/webm', 'video/3gpp', 'video/3gpp2', 'video/ogg','video/mpeg', 
                                'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-flv', 'video/x-m4v', 
                                'video/x-ms-wmv', 
                                'audio/midi', 'audio/mpeg', 'audio/webm', 'audio/ogg', 'audio/wav', 
                                'audio/vnd.wave', 'audio/x-ms-wma']

        # Export directory
        exportDirectory = Case.getCurrentCase().getExportDirectory()
        caseName = Case.getCurrentCase().getName()
        number = Case.getCurrentCase().getNumber()

        exportDirectory = os.path.join(exportDirectory, str(number) + "AutopsyToGriffeye")
        self.log(Level.INFO, "==> 2) exportDirectory=" + str(exportDirectory) + " caseName=" + str(caseName) + " number=" + str(number))
        try: 
                os.mkdir(exportDirectory)
        except:
                pass


	# Image XML file
        xmlFileImages = os.path.join(exportDirectory, str(number) + str(number) + "_images.xml")
        xmlFileVideoes = os.path.join(exportDirectory, str(number) + str(number) + "_videoes.xml");

        f = open(xmlFileImages, "w")
        f.write('<?xml version="1.0" encoding="utf-16"?>\n')
        f.close()

        f = open(xmlFileImages, "a")
        f.write('	<ReportIndex version="2.0" source="Autopsy" dll="Autopsy To Griffeye 1.4">\n')
        f.close()

        f = open(xmlFileVideoes, "w")
        f.write('<?xml version="1.0" encoding="utf-16"?>\n')
        f.close()

        f = open(xmlFileVideoes, "a")
        f.write('	<ReportIndex version="2.0" source="Autopsy" dll="Autopsy To Griffeye 1.4">\n')
        f.close()

	# Pass parameter
	self.exportDirectoryGlobal = exportDirectory;
	self.xmlFileImagesGlobal = xmlFileImages;
	self.xmlFileVideoesGlobal = xmlFileVideoes;

	# Write data to log for debug
	self.log(Level.INFO, "==> Autopsy To Griffeye start info: exportDirectory=" + str(exportDirectory) + " xmlFileImages=" + str(xmlFileImages) + " xmlFileVideoes=" + str(xmlFileVideoes))

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
        if(file.getMIMEType() in self.listOfImagesMimeToCopy):

		# XML fullpath
		xmlFullpath = file.getUniquePath().replace("/", "\\")
		xmlHash = file.getMd5Hash()

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
                extractedFile = os.path.join(pathToCreate, file.getName())
                try:
                        ContentUtils.writeToFile(file, File(extractedFile))
                except:
                        self.log(Level.SEVERE, "Error writing File " + file.getName() + " to " + extractedFile)


		# Write image to XML file
                try:
                        f = open(self.xmlFileImagesGlobal, "a")
                        f.write("		<Image>\n")
                        f.write("			<path><![CDATA[Files\]]></path>\n")
                        f.write("			<picture>+ str(xmlHash) +</picture>\n")
                        f.write("			<category>0</category>\n")
                        f.write("			<id>0</id>\n")
                        f.write("			<fileoffset>0</fileoffset>\n")
                        f.write("			<fullpath><![CDATA[" + str(xmlFullpath) + "]]></fullpath>\n")
                        f.write("			<created>1242837627</created>\n")
                        f.write("			<accessed>1242837627</accessed>\n")
                        f.write("			<written>1237311720</written>\n")
                        f.write("			<deleted>0</deleted>\n")
                        f.write("			<hash>" + str(xmlHash) + "</hash>\n")
                        f.write("			<encaseHash>0</encaseHash>\n")
                        f.write("			<myDescription>Existing</myDescription>\n")
                        f.write("			<physicalLocation>43680</physicalLocation>\n")
                        f.write("			<myUnique>0</myUnique>\n")
                        f.write("			<tagged>0</tagged>\n")
                        f.write("			<subCat></subCat>\n")
                        f.write("			<notes></notes>\n")
                        f.write("			<fileSize>3501981</fileSize>\n")
                        f.write("			<bitDepth></bitDepth>\n")
                        f.write("			<aspectRatio></aspectRatio>\n")
                        f.write("		</Image>\n")
                        f.close()
                except:
                        self.log(Level.SEVERE, "Error could not append to XML file " + xmlFileImagesGlobal)

                # Make artifact on blackboard
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT)
                att = BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SET_NAME, AutopsyToGriffeyeFactory.moduleName, "Images")
                art.addAttribute(att)

                # Index artifact
                try:
                        # index the artifact for keyword search
                        blackboard.indexArtifact(art)
                except Blackboard.BlackboardException as e:
                        self.log(Level.SEVERE, "Error indexing artifact " + art.getDisplayName())

                # UI
                IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent(AutopsyToGriffeyeFactory.moduleName, BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT, None))

        return IngestModule.ProcessResult.OK

    # Shutdown
    def shutDown(self):
        # As a final part of this example, we'll send a message to the ingest inbox with the number of files found (in this thread)
        message = IngestMessage.createMessage(
            IngestMessage.MessageType.DATA, AutopsyToGriffeyeFactory.moduleName,
                str(self.filesFound) + " files found")
        ingestServices = IngestServices.getInstance().postMessage(message)
