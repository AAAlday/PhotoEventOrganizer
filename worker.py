from os import rename, path, makedirs, scandir
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QObject, Qt, QTimer, QDate

supportedVideoFormats = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".rm", ".ogv", ".ts", ".vob", ".divx", ".xvid", ".amv"]
supportedImageFormats = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg", ".eps", ".ico", ".raw", ".ai", ".exr"]

class Worker(QObject): # QObject makes this class pure-logic only class while still being able to use some widgets
    def __init__(self, inputLayout, mediaLayout, buttonsLayout, parentWidget):
        super().__init__()
        self.inputLayout = inputLayout
        self.mediaLayout = mediaLayout
        self.buttonsLayout = buttonsLayout
        self.parentWidget = parentWidget
        self.mediaLocationTextBox = self.inputLayout.mediaLocationTextBox
        self.mediaDestinationTextBox = self.inputLayout.mediaDestinationTextBox
        self.mediaCodeComboBox = self.inputLayout.mediaCodeComboBox
        self.eventDirectoryNameComboBox = self.inputLayout.eventDirectoryNameComboBox
        self.mediaCode = self.inputLayout.mediaCodeComboBox
        self.mediaList = self.mediaLayout.mediaList
        self.eventCalendar = self.inputLayout.eventCalendar
        self.eventCalendar.setDate(QDate(2025, 5, 1)) # For debugging purposes
        self.eventMonths = ["January", "February", "March", "April",
                        "May", "June", "July", "August",
                        "September", "October", "November", "December"]
        self.__previousMonthYear = f"{str(self.eventCalendar.date().year())}-{str(self.eventCalendar.date().month())}" # Only usable within this class, invisible outside
        self.showButton = self.buttonsLayout.showButton
        self.doesMemoryExists = self.parentWidget.doesMemoryExists

        # Fetch media code collection if present
        if self.doesMemoryExists:
            with open("assets/memory/mediaCodeCollection.peomc", "r") as mediaCodeFile:
                for mediaCode in mediaCodeFile:
                    mediaCode = ''.join(mediaCode.split()) # Removes white spaces including new line for proper displayment. Comment this line and see for yourself
                    self.mediaCodeComboBox.addItem(mediaCode)
    
    def renameMedia(self):
        inputComplete = self.mediaLocationTextBox.text() != "" and self.mediaDestinationTextBox.text() != "" and self.eventDirectoryNameComboBox.currentText() != "" and self.mediaCode.currentText() != "" # Determines if all required inputs are complete

        # Only rename if all required inputs are complete
        if inputComplete:
            mediaToBeRenamed = scandir(self.mediaLocationTextBox.text()) # From os.scandir
            sortedMediaToBeRenamed = list(sorted(mediaToBeRenamed, key=lambda e: e.stat().st_mtime)) # Sort media based on last modified time, oldest on top and newest on bottom.
            mediaToBeRenamedCount = len([mediaFile for mediaFile in sortedMediaToBeRenamed if mediaFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats))]) # Counts all supported media files

            yearDirectory, monthDirectory, eventDirectory = self.getTargetDirectory()
            fullNewMediaDestinationDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}/{eventDirectory}"
            mediaNumberStartingCount = self.getCurrentNumberOfMedia(fullNewMediaDestinationDirectory) + 1

            if mediaToBeRenamedCount > 0: # There is at least 1 supported media file to be renamed
                if not path.isdir(fullNewMediaDestinationDirectory): # Make directory if it does not exists yet
                    makedirs(fullNewMediaDestinationDirectory) # From os.makedirs; makedirs instead of mkdir for nested directories

                for mediaFile in sortedMediaToBeRenamed:
                    oldMediaName = f"{self.mediaLocationTextBox.text()}/{mediaFile.name}"
                    _, newMediaNameExtension = path.splitext(oldMediaName) # From os.path; Get the file extension and ignore root directory
                    
                    if mediaFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only renames supported media files
                        newMediaName = f"{fullNewMediaDestinationDirectory}/{self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}"
                        rename(oldMediaName, newMediaName) # From os.rename
                        print(f"{mediaFile.name} successfully renamed to {self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}")
                        mediaNumberStartingCount += 1
                
                # Cleans media list and media viewer
                self.mediaList.clear()
                self.cleanMediaViewer()

                self.showButton.setText("SHOW MEDIA\nDESTINATION")
                print("\nRenaming media complete!")
                QTimer.singleShot(50, lambda: QMessageBox.information(self.buttonsLayout, "Operation Successful!", "Renaming media complete!")) # Delays the notification to flush the widgets inside the media container (self.mediaLayout.mediaBox) by 50ms
            else:
                QMessageBox.warning(self.buttonsLayout, "Operation Failed!", "Media Location directory is empty! No media to be renamed.")
        else:
            QMessageBox.warning(self.buttonsLayout, "Operation Failed!", "Make sure all required information are available!")

    def getCurrentNumberOfMedia(self, fullNewMediaDestinationDirectory):
        mediaCount = 0
        
        if path.exists(fullNewMediaDestinationDirectory):
                # Counts the collected media files in the media destination directory
                mediaCount = len([mediaFile for mediaFile in scandir(fullNewMediaDestinationDirectory) if mediaFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats))])
        
        return mediaCount

    def showDirectoryContents(self):
        inputComplete = self.mediaLocationTextBox.text() != "" and self.mediaDestinationTextBox.text() != "" and self.eventDirectoryNameComboBox.currentText() != "" and self.mediaCode.currentText() != "" # Determines if all required inputs are complete

        if inputComplete:
            self.mediaList.clear() # Refreshes the media list items

            if self.showButton.text() == "SHOW MEDIA\nDESTINATION":
                yearDirectory, monthDirectory, eventDirectory = self.getTargetDirectory()
                fullNewMediaDestinationDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}/{eventDirectory}"

                if path.exists(f"{fullNewMediaDestinationDirectory}"): # This means media from media location were already renamed and moved to media destination
                    scannedItems = scandir(fullNewMediaDestinationDirectory) # From os.scandir
                
                    sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_ctime)) # Sort items based on most recent renamed files, oldest on top and newest on bottom.

                    for validFile in sortedScannedItems:
                        if validFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only accepts supported image and video files
                            self.mediaList.addItem(validFile.name)
                    
                self.showButton.setText("SHOW MEDIA\nLOCATION")
            else:
                scannedItems = scandir(self.mediaLocationTextBox.text()) # From os.scandir
                sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # Sort items based on last modification time, oldest on top and newest on bottom.

                for validFile in sortedScannedItems:
                    if validFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only accepts supported image and video files
                        self.mediaList.addItem(validFile.name)
                
                self.showButton.setText("SHOW MEDIA\nDESTINATION")
        else:
            QMessageBox.warning(self.parentWidget, "Operation Failed!", "Make sure all required information are available!")
    
    def browseMediaLocationClicked(self):
        selectedDirectory = QFileDialog.getExistingDirectory(self.inputLayout, "Media Location Directory")

        if selectedDirectory:
            self.mediaLocationTextBox.setText(selectedDirectory)
            self.mediaList.clear()
            scannedItems = scandir(selectedDirectory) # From os.scandir
            sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # Sort items based on last modification time, oldest on top and newest on bottom.

            for validFile in sortedScannedItems:
                if validFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only accepts supported image and video files
                    self.mediaList.addItem(validFile.name)
    
    def browseMediaDestinationClicked(self):
        selectedDirectory = QFileDialog.getExistingDirectory(self.inputLayout, "Media Destination Directory")

        if selectedDirectory:
            self.mediaDestinationTextBox.setText(selectedDirectory)
    
    def addNewMediaCode(self):
        newCode, codeAdded = QInputDialog.getText(self.inputLayout, "New Media Code", "Keep it short.") # newCode = string (code name itself); codeAdded = boolean value (True or False)
        
        if newCode and codeAdded:
            if self.doesMemoryExists: # Appends media code to existing memory file
                with open("assets/memory/mediaCodeCollection.peomc", "a") as mediaCodeFile:
                    currentMediaCodes = [self.mediaCodeComboBox.itemText(mediaCodeIndex) for mediaCodeIndex in range(self.mediaCodeComboBox.count())] # Makes a list out of the media codes in self.mediaCodeComboBox

                    if newCode.upper() in currentMediaCodes: # Rejects new media code if it already exists
                        QMessageBox.warning(self.inputLayout, "Operation Failed!", "Media code already exists.")
                    else:
                        self.mediaCodeComboBox.addItem(newCode.upper())
                        mediaCodeFile.write("\n" + newCode.upper())
                        QMessageBox.information(self.inputLayout, "Operation Successful!", "New media code has been added.")
            else: # Will create fresh memory file and writes media code
                with open("assets/memory/mediaCodeCollection.peomc", "w") as mediaCodeFile:
                    mediaCodeFile.write(newCode.upper())
                    self.memoryExists = True
        else:
            QMessageBox.information(self.inputLayout, "Operation Failed!", "Operation has been cancelled.")
    
    def imageSelected(self):
        currentItemSelected = self.mediaList.currentItem()
        if self.showButton.text() == "SHOW MEDIA\nLOCATION": # The user is currently viewing contents of media destination directory
            yearDirectory, monthDirectory, eventDirectory = self.getTargetDirectory()
            targetMediaDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}/{eventDirectory}"
        else: # The user is currently viewing contents of media location directory
            targetMediaDirectory = self.mediaLocationTextBox.text()
        
        self.cleanMediaViewer()
        
        if currentItemSelected is not None:
            imageItem = self.mediaList.currentItem().text()

            if targetMediaDirectory:
                mediaPath = f"{targetMediaDirectory}/{imageItem}"

                if mediaPath.lower().endswith(tuple(supportedImageFormats)): # Show supported media
                    mediaPixmap = QPixmap(mediaPath)
                else: # No preview
                    mediaPixmap = QPixmap("assets/images/no_preview.png")
                
                self.mediaLabel = ResponsiveMedia(mediaPixmap) # Contains the adjusted pixmap itself
                self.mediaLayout.mediaBox.addWidget(self.mediaLabel) # QVBoxLayout where the adjusted pixmap is stored
                self.mediaLayout.mediaBoxFrame.setLayout(self.mediaLayout.mediaBox) # QFrame where the QVBoxLayout is stored for framing purposes
    
    def cleanMediaViewer(self):
        # Deletes all widgets added to mediaBox layout
        while self.mediaLayout.mediaBox.count():
            item = self.mediaLayout.mediaBox.takeAt(0)
            itemWidget = item.widget()
            
            if itemWidget is not None:
                itemWidget.deleteLater()
    
    def showEventDirectories(self):
        yearDirectory, monthDirectory, _ = self.getTargetDirectory()
        targetDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}"
        currentMonthYear = f"{str(self.eventCalendar.date().year())}-{str(self.eventCalendar.date().month())}"

        if self.__previousMonthYear != currentMonthYear:
            self.eventDirectoryNameComboBox.blockSignals(True) # Temporarily block signals to avoid calling adjustEventDate() twice
            self.eventDirectoryNameComboBox.clear() # This can trigger adjustEventDate() unintentionally as it removes all items inside eventDirectoryNameComboBox which triggers currentIndexChanged() event
            self.eventDirectoryNameComboBox.blockSignals(False) # Reconnects to adjustEventDate()
            self.addEventDirectories(targetDirectory)
        else:
            if self.__previousMonthYear == currentMonthYear and self.eventDirectoryNameComboBox.count() == 0:
                self.addEventDirectories(targetDirectory)
            else:
                self.mediaList.clear()
    
    def addEventDirectories(self, targetDirectory, eventDirectoryCounter=0):
        if path.exists(targetDirectory):
            scannedItems = scandir(targetDirectory)
            sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # List all directories based from last modified (creation) date. Oldest on top, newest on bottom
            scannedDirectoriesCount = len([mediaDirectory for mediaDirectory in sortedScannedItems if mediaDirectory.is_dir()])

            for scannedItem in sortedScannedItems:
                if scannedItem.is_dir():
                    eventName = scannedItem.name[12:]
                    eventIndex = eventDirectoryCounter
                    eventYear = int(scannedItem.name[0:4])
                    eventMonth = int(scannedItem.name[5:7])
                    eventDay = int(scannedItem.name[8:10])
                    self.eventDirectoryNameComboBox.addItem(eventName, {"index": eventIndex, "date": (eventYear, eventMonth, eventDay)})
                    eventDirectoryCounter += 1
            
            if scannedDirectoriesCount > 0:
                self.eventDirectoryNameComboBox.setCurrentIndex(0)
        
    def adjustEventDate(self):
        eventData = self.eventDirectoryNameComboBox.currentData()
        eventYear, eventMonth, eventDay = eventData["date"]

        self.eventCalendar.blockSignals(True) # Temporarily block signals to avoid calling showEventDirectories() twice
        self.eventCalendar.setDate(QDate(eventYear, eventMonth, eventDay)) # This can trigger showEventDirectories() unintentionally because this changes the date in QDateEdit (eventCalendar GUI widget) with setDate() which triggers dateChanged() event
        self.__previousMonthYear = f"{str(self.eventCalendar.date().year())}-{str(self.eventCalendar.date().month())}"
        self.eventCalendar.blockSignals(False) # Reconnects to showEventDirectories()

        mediaDestinationRootDirectory = self.mediaDestinationTextBox.text()
        eventMonthName = self.eventMonths[eventMonth - 1]
        eventDirectoryName = f"{self.eventCalendar.text()}: {self.eventDirectoryNameComboBox.currentText()}"
        targetDirectory = f"{mediaDestinationRootDirectory}/{eventYear}/{eventMonthName}/{eventDirectoryName}"
        
        self.mediaList.clear()

        if self.showButton.text() == "SHOW MEDIA\nLOCATION" and path.exists(targetDirectory):
            self.addMediaListItems(targetDirectory)
        else:
            self.addMediaListItems(self.mediaLocationTextBox.text())

    def getTargetDirectory(self):
        yearDirectory = self.eventCalendar.date().year()
        monthDirectory = self.eventMonths[self.eventCalendar.date().month() - 1]
        eventDirectory = f"{self.eventCalendar.text()}: {self.eventDirectoryNameComboBox.currentText()}"

        return yearDirectory, monthDirectory, eventDirectory

    def addMediaListItems(self, targetDirectory):
        self.mediaList.clear()
        scannedItems = scandir(targetDirectory) # From os.scandir
        sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # Sort items based on last modification time, oldest on top and newest on bottom.

        for validFile in sortedScannedItems:
            if validFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only accepts supported image and video files
                self.mediaList.addItem(validFile.name)

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