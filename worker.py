from os import rename, path, makedirs, scandir, walk
from shutil import move
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
        self.eventMonths = ["January", "February", "March", "April",
                        "May", "June", "July", "August",
                        "September", "October", "November", "December"]
        self.__eventDatesCollection = {} # Event dates container of current media root destination for event name referencing based on dates
        self.showButton = self.buttonsLayout.showButton
        self.doesMemoryExists = self.parentWidget.doesMemoryExists # Flag that determines if media code collection file is already present or not yet
        self.eventDirectoryNameChangedWithDropDown = True # Flag that handles media viewer automatically being refreshed when clicking eventDirectoryNameComboBox because its text was set programmatically after selecting date instead of setting the text with dropdown

        # Fetch media code collection if present
        if self.doesMemoryExists:
            with open("assets/memory/mediaCodeCollection.peomc", "r") as mediaCodeFile:
                for mediaCode in mediaCodeFile:
                    mediaCode = ''.join(mediaCode.split()) # Removes white spaces including new line for proper displayment. Comment this line and see for yourself
                    self.mediaCodeComboBox.addItem(mediaCode)
    
    def browseMediaLocationClicked(self):
        selectedDirectory = QFileDialog.getExistingDirectory(self.inputLayout, "Media Location Directory")

        if selectedDirectory: # selectedDirectory is not an empty string
            self.mediaLocationTextBox.setText(selectedDirectory)
            self.mediaList.clear()
            self.addMediaListItems(selectedDirectory)
    
    def addMediaListItems(self, targetDirectory):
        self.mediaList.clear()

        if path.exists(targetDirectory):
            scannedItems = scandir(targetDirectory) # From os.scandir
            sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # Sort items based on last modification time, oldest on top and newest on bottom.

            for validFile in sortedScannedItems:
                if validFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only accepts supported image and video files
                    self.mediaList.addItem(validFile.name)
    
    def browseMediaDestinationClicked(self):
        selectedDirectory = QFileDialog.getExistingDirectory(self.inputLayout, "Media Destination Directory")

        if selectedDirectory: # selectedDirectory is not an empty string
            self.mediaDestinationTextBox.setText(selectedDirectory)

    def showEventDirectories(self): # Get back here laturr
        yearDirectory, monthDirectory, _ = self.getTargetDirectory()
        eventYear, eventMonth, eventDay = self.eventCalendar.date().year(), self.eventCalendar.date().month(), self.eventCalendar.date().day()
        targetDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}"

        self.eventDirectoryNameComboBox.clear()
        self.addEventDirectories(targetDirectory)

        if self.showButton.text() == "SHOW MEDIA\nLOCATION":
            if f"{eventYear}-{eventMonth}-{eventDay}" in self.__eventDatesCollection.keys():
                eventDirectory = f"{targetDirectory}/{self.eventCalendar.text()}: {self.__eventDatesCollection[f"{eventYear}-{eventMonth}-{eventDay}"]}"

                if path.exists(eventDirectory):
                    self.eventDirectoryNameComboBox.setCurrentText(self.__eventDatesCollection[f"{eventYear}-{eventMonth}-{eventDay}"])
                    self.eventDirectoryNameChangedWithDropDown = False
                    self.addMediaListItems(eventDirectory)
                else:
                    # self.eventDirectoryNameComboBox.setCurrentText()
                    self.mediaList.clear()
                    self.eventDirectoryNameComboBox.clear()
            else:
                self.mediaList.clear()
                self.eventDirectoryNameComboBox.setCurrentText("")
        else:
            if f"{eventYear}-{eventMonth}-{eventDay}" in self.__eventDatesCollection.keys():
                eventDirectory = f"{targetDirectory}/{self.eventCalendar.text()}: {self.__eventDatesCollection[f"{eventYear}-{eventMonth}-{eventDay}"]}"

                if path.exists(eventDirectory):
                    self.eventDirectoryNameComboBox.setCurrentText(self.__eventDatesCollection[f"{eventYear}-{eventMonth}-{eventDay}"])
                    self.eventDirectoryNameChangedWithDropDown = False
                else:
                    self.eventDirectoryNameComboBox.setCurrentText("")

            else:
                self.eventDirectoryNameComboBox.setCurrentText("")

    def getTargetDirectory(self):
        yearDirectory = self.eventCalendar.date().year()
        monthDirectory = self.eventMonths[self.eventCalendar.date().month() - 1]
        eventDirectory = f"{self.eventCalendar.text()}: {self.eventDirectoryNameComboBox.currentText()}"

        return yearDirectory, monthDirectory, eventDirectory
    
    def addEventDirectories(self, targetDirectory, eventDirectoryCounter=0):
        if path.exists(targetDirectory):
            scannedItems = scandir(targetDirectory)
            sortedScannedItems = list(sorted(scannedItems, key=lambda e: e.stat().st_mtime)) # List all directories based from last modified (creation) date. Oldest on top, newest on bottom
            self.eventDirectoryNameComboBox.addItem("")
            self.__eventDatesCollection.clear()

            for scannedItem in sortedScannedItems:
                if scannedItem.is_dir():
                    eventName = scannedItem.name[12:]
                    eventYear = int(scannedItem.name[0:4])
                    eventMonth = int(scannedItem.name[5:7])
                    eventDay = int(scannedItem.name[8:10])
                    
                    self.eventDirectoryNameComboBox.addItem(eventName, {"date": (eventYear, eventMonth, eventDay)})
                    self.__eventDatesCollection[f"{eventYear}-{eventMonth}-{eventDay}"] = eventName # Dictionary as reference for automatically setting event directory name when an event happened in the chosen event date
    
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
    
    def adjustEventDate(self):
        if self.eventDirectoryNameComboBox.currentText(): # eventDirectoryName text is not an empty string
            eventData = self.eventDirectoryNameComboBox.currentData()
            eventYear, eventMonth, eventDay = eventData["date"]
            self.eventCalendar.blockSignals(True) # Temporarily block signals to avoid calling showEventDirectories() twice
            self.eventCalendar.setDate(QDate(eventYear, eventMonth, eventDay)) # This can trigger showEventDirectories() unintentionally because this changes the date in QDateEdit (eventCalendar GUI widget) with setDate() which triggers dateChanged() event
            self.eventCalendar.blockSignals(False) # Reconnects to showEventDirectories()
            mediaDestinationRootDirectory = self.mediaDestinationTextBox.text()
            eventMonthName = self.eventMonths[eventMonth - 1]
            eventDirectoryName = f"{self.eventCalendar.text()}: {self.eventDirectoryNameComboBox.currentText()}"
            targetDirectory = f"{mediaDestinationRootDirectory}/{eventYear}/{eventMonthName}/{eventDirectoryName}"

            if self.showButton.text() == "SHOW MEDIA\nLOCATION" and self.eventDirectoryNameChangedWithDropDown:
                self.addMediaListItems(targetDirectory)

            self.eventDirectoryNameChangedWithDropDown = True
        else:
            self.eventCalendar.blockSignals(True) # Temporarily block signals to avoid calling showEventDirectories() twice
            self.eventCalendar.setDate(QDate().currentDate()) # This can trigger showEventDirectories() unintentionally because this changes the date in QDateEdit (eventCalendar GUI widget) with setDate() which triggers dateChanged() event
            self.eventCalendar.blockSignals(False) # Reconnects to showEventDirectories()
            
            if self.showButton.text() == "SHOW MEDIA\nLOCATION":
                self.mediaList.clear()
    
    def imageSelected(self):
        currentItemSelected = self.mediaList.currentItem()
        self.cleanMediaViewer()

        if self.showButton.text() == "SHOW MEDIA\nLOCATION": # The user is currently viewing contents of media destination directory
            yearDirectory, monthDirectory, eventDirectory = self.getTargetDirectory()
            targetMediaDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}/{eventDirectory}"
        else: # The user is currently viewing contents of media location directory
            targetMediaDirectory = self.mediaLocationTextBox.text()
        
        if currentItemSelected is not None: # User successfully selected an item
            imageItem = self.mediaList.currentItem().text()

            if targetMediaDirectory: # targetMediaDirectory is not an empty string
                mediaPath = f"{targetMediaDirectory}/{imageItem}"

                if mediaPath.lower().endswith(tuple(supportedImageFormats)): # Show supported media (images only for now)
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
    
    def renameMedia(self):
        inputComplete = self.mediaLocationTextBox.text() != "" and self.mediaDestinationTextBox.text() != "" and self.eventDirectoryNameComboBox.currentText() != "" and self.mediaCode.currentText() != "" # Determines if all required inputs are complete

        # Only rename if all required inputs are complete
        if inputComplete:
            mediaToBeRenamed = scandir(self.mediaLocationTextBox.text()) # From os.scandir
            sortedMediaToBeRenamed = list(sorted(mediaToBeRenamed, key=lambda e: e.stat().st_mtime)) # Sort media based on last modified time, oldest on top and newest on bottom.
            mediaToBeRenamedCount = len([mediaFile for mediaFile in sortedMediaToBeRenamed if mediaFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats))]) # Counts all supported media files
            yearDirectory, monthDirectory, eventDirectory = self.getTargetDirectory()
            fullNewMediaDestinationDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}/{eventDirectory}"
            mediaNumberStartingCount = self.getCurrentNumberOfMedia(self.mediaLocationTextBox.text(), self.mediaDestinationTextBox.text()) + 1

            if mediaToBeRenamedCount > 0: # There is at least 1 supported media file to be renamed
                if not path.isdir(fullNewMediaDestinationDirectory): # Make directory if it does not exists yet
                    makedirs(fullNewMediaDestinationDirectory) # From os.makedirs; makedirs instead of mkdir for nested directories

                for mediaFile in sortedMediaToBeRenamed:
                    oldMediaName = f"{self.mediaLocationTextBox.text()}/{mediaFile.name}"
                    _, newMediaNameExtension = path.splitext(oldMediaName) # From os.path; Get the file extension and ignore root directory
                    
                    if mediaFile.name.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)): # Only renames supported media files
                        newMediaName = f"{fullNewMediaDestinationDirectory}/{self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}"

                        # Handles moving and renaming files with care
                        try:
                            rename(oldMediaName, newMediaName) # From os.rename
                            print(f"{mediaFile.name} successfully renamed to {self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}")
                            mediaNumberStartingCount += 1
                        except OSError as ose: # OS related errors
                            if ose.errno == 18: # Invalid cross-device link
                                move(oldMediaName, newMediaName) # From shutil.move (fallback if rename() didn't work)
                                print(f"{mediaFile.name} successfully renamed to {self.mediaCode.currentText()}_{str(mediaNumberStartingCount)}{newMediaNameExtension}")
                                mediaNumberStartingCount += 1
                            else:
                                print(f"The error code is: {ose.errno}")
                        except Exception as e: # General error catching
                            print(f"You got an error: {e}")
                
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

    def getCurrentNumberOfMedia(self, mediaLocationDirectory, mediaRootDirectory):
        mediaCount = 0

        # rootDirectory = current directory being browsed
        # mediaFiles = files under rootDirectory
        for rootDirectory, _, mediaFiles in walk(mediaRootDirectory):
            if rootDirectory != mediaLocationDirectory: # Count items inside if the current directory being browsed and the mediaLocationDirectory are not the same (use case: only renaming files)
                for mediaFile in mediaFiles:
                    if mediaFile.lower().endswith(tuple(supportedImageFormats + supportedVideoFormats)):
                        mediaCount += 1
        
        return mediaCount

    def showDirectoryContents(self):
        inputComplete = self.mediaLocationTextBox.text() != "" and self.mediaDestinationTextBox.text() != "" and self.eventDirectoryNameComboBox.currentText() != "" and self.mediaCode.currentText() != "" # Determines if all required inputs are complete

        if inputComplete:
            self.mediaList.clear() # Refreshes the media list items

            if self.showButton.text() == "SHOW MEDIA\nDESTINATION":
                yearDirectory, monthDirectory, eventDirectory = self.getTargetDirectory()
                fullNewMediaDestinationDirectory = f"{self.mediaDestinationTextBox.text()}/{yearDirectory}/{monthDirectory}/{eventDirectory}"

                if path.exists(f"{fullNewMediaDestinationDirectory}"): # This means media from media location were already renamed and moved to media destination
                    self.addMediaListItems(fullNewMediaDestinationDirectory)
                    
                self.showButton.setText("SHOW MEDIA\nLOCATION")
            else:
                self.addMediaListItems(self.mediaLocationTextBox.text())
                self.showButton.setText("SHOW MEDIA\nDESTINATION")
        else:
            QMessageBox.warning(self.parentWidget, "Operation Failed!", "Make sure all required information are available!")

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