from os import walk, rename, path, makedirs, scandir
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QObject, Qt, QTimer

supportedFormats = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg", ".eps", ".raw") # Tuple of supported files

class Worker(QObject): # QObject makes this class pure-logic only class while still being able to use some widgets
    def __init__(self, inputLayout, mediaLayout, buttonsLayout, parentWidget):
        super().__init__()
        self.inputLayout = inputLayout
        self.mediaLayout = mediaLayout
        self.parentWidget = parentWidget
        self.mediaLocationTextBox = inputLayout.mediaLocationTextBox
        self.mediaDestinationTextBox = inputLayout.mediaDestinationTextBox
        self.mediaCodeComboBox = inputLayout.mediaCodeComboBox
        self.eventFolderNameTextBox = inputLayout.eventFolderNameTextBox
        self.mediaCode = inputLayout.mediaCodeComboBox
        self.mediaList = mediaLayout.mediaList
        self.eventCalendar = inputLayout.eventCalendar
        self.eventMonths = ["January", "February", "March", "April",
                        "May", "June", "July", "August",
                        "September", "October", "November", "December"]
        self.showButton = buttonsLayout.showButton
        self.doesMemoryExists = parentWidget.doesMemoryExists

        # Fetch media code collection if present
        if self.doesMemoryExists:
            with open("assets/memory/mediaCodeCollection.peomc", "r") as mediaCodeFile:
                for mediaCode in mediaCodeFile:
                    mediaCode = ''.join(mediaCode.split()) # Removes white spaces including new line for proper displayment. Comment this line and see for yourself
                    self.mediaCodeComboBox.addItem(mediaCode)
    
    def renameMedia(self):
        inputComplete = self.mediaLocationTextBox.text != "" and self.mediaDestinationTextBox.text() != "" and self.eventFolderNameTextBox.text() != "" and self.mediaCode.currentText() != "" # Determines if all required inputs are complete

        # Only rename if all required inputs are complete
        if inputComplete:
            mediaToBeRenamed = scandir(self.mediaLocationTextBox.text()) # From os.scandir
            sortedMediaToBeRenamed = list(sorted(mediaToBeRenamed, key=lambda e: e.stat().st_mtime)) # Sort media based on last modified time, oldest on top and newest on bottom.
            mediaToBeRenamedCount = len(sortedMediaToBeRenamed)
            yearFolder = self.eventCalendar.date().year()
            monthFolder = self.eventMonths[self.eventCalendar.date().month() - 1]
            eventFolder = f"{self.eventCalendar.text()}: {self.eventFolderNameTextBox.text()}"
            mediaNumberStartingCount = self.getCurrentNumberOfMedia() + 1

            for mediaFile in sortedMediaToBeRenamed:
                oldMediaName = f"{self.mediaLocationTextBox.text()}/{mediaFile.name}"
                _, newMediaNameExtension = path.splitext(oldMediaName) # From os.path; Get the file extension and ignore root directory
                fullNewMediaDestinationDirectory = f"{self.mediaDestinationTextBox.text()}/{yearFolder}/{monthFolder}/{eventFolder}"

                # Make directory if it does not exists yet
                if not path.isdir(fullNewMediaDestinationDirectory):
                    makedirs(fullNewMediaDestinationDirectory) # From os.makedirs; makedirs instead of mkdir for nested directories
                
                newMediaName = f"{fullNewMediaDestinationDirectory}/{self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}"
                rename(oldMediaName, newMediaName) # From os.rename
                print(f"{mediaFile.name} successfully renamed to {self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}")
                mediaNumberStartingCount += 1
            
            # Only shows after successfully renaming at least 1 file
            if mediaToBeRenamedCount > 0:
                # Cleans media list and media viewer
                self.mediaList.clear()
                self.cleanMediaViewer()

                self.showButton.setText("SHOW MEDIA\nDESTINATION")
                print("\nRenaming media complete!")
                # QMessageBox.information(self.parentWidget, "Operation Successful!", "Renaming media complete!")
                QTimer.singleShot(50, lambda: QMessageBox.information(self.parentWidget, "Operation Successful!", "Renaming media complete!")) # Delays the notification to flush the widgets inside the media container (self.mediaLayout.mediaBox)
            else:
                QMessageBox.warning(self.parentWidget, "Operation Failed!", "Media Location directory is empty! No media to be renamed.")
        else:
            QMessageBox.warning(self.parentWidget, "Operation Failed!", "Make sure all required information are available!")

    def getCurrentNumberOfMedia(self):
        mediaCount = 0
        mediaRoot = self.mediaDestinationTextBox.text()
        
        if mediaRoot: # mediaLocationTextBox of inputLayout is not empty
            for _, _, mediaFiles in walk(mediaRoot, topdown=True): # From os.walk; Disregarding root and subdirectories, only counts number of media saved inside the root folder
                for mediaFile in mediaFiles:
                    if not mediaFile.lower().endswith(".ini"): # Temporary filter, change it with explicitly allowing picture and video files only 
                        mediaCount += 1
        
        return mediaCount

    def showDirectoryContents(self):
        inputComplete = self.mediaLocationTextBox.text != "" and self.mediaDestinationTextBox.text() != "" and self.eventFolderNameTextBox.text() != "" and self.mediaCode.currentText() != "" # Determines if all required inputs are complete

        if inputComplete:
            self.mediaList.clear() # Refreshes the media list items

            if self.showButton.text() == "SHOW MEDIA\nDESTINATION":
                yearFolder = self.eventCalendar.date().year()
                monthFolder = self.eventMonths[self.eventCalendar.date().month() - 1]
                eventFolder = f"{self.eventCalendar.text()}: {self.eventFolderNameTextBox.text()}"
                fullNewMediaDestinationDirectory = f"{self.mediaDestinationTextBox.text()}/{yearFolder}/{monthFolder}/{eventFolder}"

                if path.exists(f"{fullNewMediaDestinationDirectory}"): # This means media from media location were already renamed and moved to media destination
                    scannedItems = scandir(fullNewMediaDestinationDirectory) # From os.scandir
                else: # This means media from media location are still not renamed and moved to media destination
                    scannedItems = scandir(self.mediaDestinationTextBox.text()) # From os.scandir
                
                sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_ctime)) # Sort items based on most recent renamed files, oldest on top and newest on bottom.

                for validFile in sortedScannedItems:
                    if validFile.is_file():
                        self.mediaList.addItem(validFile.name)
                
                self.showButton.setText("SHOW MEDIA\nLOCATION")
            else:
                scannedItems = scandir(self.mediaLocationTextBox.text()) # From os.scandir
                sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # Sort items based on last modification time, oldest on top and newest on bottom.

                for validFile in sortedScannedItems:
                    if validFile.is_file():
                        self.mediaList.addItem(validFile.name)
                
                self.showButton.setText("SHOW MEDIA\nDESTINATION")
        else:
            QMessageBox.warning(self.parentWidget, "Operation Failed!", "Make sure all required information are available!")
    
    def browseMediaLocationClicked(self):
        selectedDirectory = QFileDialog.getExistingDirectory(self.inputLayout, "Select media location folder")

        if selectedDirectory:
            self.mediaLocationTextBox.setText(selectedDirectory)
            self.mediaList.clear()
            scannedItems = scandir(selectedDirectory) # From os.scandir
            sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # Sort items based on last modification time, oldest on top and newest on bottom.

            for validFile in sortedScannedItems:
                if validFile.is_file():
                    self.mediaList.addItem(validFile.name)
    
    def browseMediaDestinationClicked(self):
        selectedDirectory = QFileDialog.getExistingDirectory(self.inputLayout, "Select media destination folder")

        if selectedDirectory:
            self.mediaDestinationTextBox.setText(selectedDirectory)
    
    def addNewMediaCode(self):
        newCode, codeAdded = QInputDialog.getText(self.inputLayout, "New Media Code", "") # newCode = string (code name itself); codeAdded = boolean value (True or False)
        
        if newCode and codeAdded:
            if self.doesMemoryExists: # Appends media code to existing memory file
                with open("assets/memory/mediaCodeCollection.peomc", "a") as mediaCodeFile:
                    mediaCodeFile.write("\n" + newCode)
            else: # Will create fresh memory file and writes media code
                with open("assets/memory/mediaCodeCollection.peomc", "w") as mediaCodeFile:
                    mediaCodeFile.write(newCode)
                    self.memoryExists = True
            
            self.mediaCodeComboBox.addItem(newCode)
            QMessageBox.information(self.parentWidget, "Operation Successful!", "New media code has been added.")
        else:
            QMessageBox.information(self.parentWidget, "Operation Failed!", "Operation has been cancelled.")
    
    def imageSelected(self):
        currentItemSelected = self.mediaList.currentItem()
        
        if self.showButton.text() == "SHOW MEDIA\nLOCATION": # The user is currently viewing contents of media destination directory
            yearFolder = self.eventCalendar.date().year()
            monthFolder = self.eventMonths[self.eventCalendar.date().month() - 1]
            eventFolder = f"{self.eventCalendar.text()}: {self.eventFolderNameTextBox.text()}"

            targetMediaDirectory = f"{self.mediaDestinationTextBox.text()}/{yearFolder}/{monthFolder}/{eventFolder}"
        else: # The user is currently viewing contents of media location directory
            targetMediaDirectory = self.mediaLocationTextBox.text()
        
        self.cleanMediaViewer()
        
        if currentItemSelected is not None:
            imageItem = self.mediaList.currentItem().text()

            if targetMediaDirectory:
                mediaPath = f"{targetMediaDirectory}/{imageItem}"

                if mediaPath.lower().endswith(supportedFormats): # Show supported media
                    mediaPixmap = QPixmap(mediaPath)
                else: # No preview
                    mediaPixmap = QPixmap("assets/images/no_preview.png")
                
                # Context:
                #       self.mediaLabel: Contains the adjusted pixmap itself
                #       self.mediaLayout.mediaBox = QVBoxLayout where the adjusted pixmap is stored
                # self.mediaLayout.mediaBoxFrame = QFrame where the QVBoxLayout is stored for framing purposes
                self.mediaLabel = ResponsiveMedia(mediaPixmap)        
                self.mediaLayout.mediaBox.addWidget(self.mediaLabel)
                self.mediaLayout.mediaBoxFrame.setLayout(self.mediaLayout.mediaBox)
    
    def cleanMediaViewer(self):
        # Deletes all widgets added to mediaBox layout
        while self.mediaLayout.mediaBox.count():
            item = self.mediaLayout.mediaBox.takeAt(0)
            itemWidget = item.widget()
            
            if itemWidget is not None:
                itemWidget.deleteLater()
        
        self.mediaLayout.mediaBox.update()

class ResponsiveMedia(QLabel):
    # Gets executed upon creating an instance of the class
    def __init__(self, originalMedia: QPixmap):
        super().__init__()
        self.originalMedia = originalMedia
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def resizeEvent(self, event):
        if self.originalMedia:
            scaledMedia = self.originalMedia.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(scaledMedia)
        
        super().resizeEvent(event)