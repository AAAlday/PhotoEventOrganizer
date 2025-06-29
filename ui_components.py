from os import path
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QListWidget, QFrame, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QDate
from worker import Worker
from utils import getResourcePath

class ApplicationWindow(QWidget):
    # Gets executed upon creating an instance of the class
    def __init__(self, geometry):
        super().__init__()
        self.setFocus()
        self.title = "Photo Event Organizer"
        self.left = int(geometry.width() * 0.25)
        self.top = int(geometry.height() * 0.2)
        self.width = int(geometry.width() * 0.5)
        self.height = int(geometry.height() * 0.6)
        self.icon = getResourcePath("assets/images/app_icon.png")
        self.memory = getResourcePath("assets/memory/mediaCodeCollection.peomc") # PEOMC stands for Photo Event Organizer Media Code
        self.doesMemoryExists = path.exists(self.memory) # From os.path
        self.createAppWindow()
    
    def createAppWindow(self):
        # App window layout
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon))

        # Creating main layout
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setRowStretch(0, 3)
        self.mainLayout.setRowStretch(1, 6)
        self.mainLayout.setRowStretch(2, 1)

        # Creating sub layouts of the main layout (input section, media viewer section, action buttons area)
        self.inputLayout = InputLayout()
        self.mediaLayout = MediaLayout()
        self.buttonsLayout = ActionButtons()

        # Setting up worker class
        self.worker = Worker(self.inputLayout, self.mediaLayout, self.buttonsLayout, self)

        # Configuring InputLayout class events
        self.inputLayout.browseMediaLocation.clicked.connect(self.worker.browseMediaLocationClicked)
        self.inputLayout.browseMediaDestination.clicked.connect(self.worker.browseMediaDestinationClicked)
        self.inputLayout.mediaDestinationTextBox.textChanged.connect(self.worker.showEventDirectories)
        self.inputLayout.addMediaCode.clicked.connect(self.worker.addNewMediaCode)
        self.inputLayout.eventCalendar.dateChanged.connect(self.worker.showEventDirectories)
        self.inputLayout.eventDirectoryNameComboBox.activated.connect(self.worker.adjustEventDate) # Only gets triggered when eventDirectoryName text was changed with dropdown

        # Configuring MediaLViewer class events
        self.mediaLayout.mediaList.currentItemChanged.connect(self.worker.imageSelected)

        # Configuring ActionButtons class events
        self.buttonsLayout.renameButton.clicked.connect(self.worker.renameMedia)
        self.buttonsLayout.showButton.clicked.connect(self.worker.showDirectoryContents)

        # Adding media and input layouts to the main layout 
        self.mainLayout.addWidget(self.inputLayout, 0, 0)
        self.mainLayout.addWidget(self.mediaLayout, 1, 0)
        self.mainLayout.addWidget(self.buttonsLayout, 2, 0)
    
class InputLayout(QWidget):
    # Gets executed upon creating an instance of the class
    def __init__(self):
        super().__init__()
        self.inputLayout = QGridLayout()
        self.setLayout(self.inputLayout)
        self.addContents()
        self.inputLayout.setVerticalSpacing(15)
        self.inputLayout.setHorizontalSpacing(20)
    
    def addContents(self):
        # Input labels
        self.mediaLocationLabel = QLabel("Media Location:")
        self.mediaDestinationLabel = QLabel("Media Root Destination:")
        self.mediaCodeLabel = QLabel("Media Code:")
        self.eventDateLabel = QLabel("Event Date:")
        self.eventDirectoryNameLabel = QLabel("Directory Name:")
        self.inputLayout.addWidget(self.mediaLocationLabel, 0, 0)
        self.inputLayout.addWidget(self.mediaDestinationLabel, 1, 0)
        self.inputLayout.addWidget(self.mediaCodeLabel, 2, 0)
        self.inputLayout.addWidget(self.eventDateLabel, 3, 0)
        self.inputLayout.addWidget(self.eventDirectoryNameLabel, 4, 0)

        # Input text box
        self.mediaLocationTextBox = QLineEdit(self)
        self.mediaLocationTextBox.setReadOnly(True)
        self.mediaDestinationTextBox = QLineEdit(self)
        self.mediaDestinationTextBox.setReadOnly(True)
        self.eventDirectoryNameComboBox = QComboBox(self)
        self.eventDirectoryNameComboBox.setEditable(True)
        self.mediaLocationTextBox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.inputLayout.addWidget(self.mediaLocationTextBox, 0, 1)
        self.inputLayout.addWidget(self.mediaDestinationTextBox, 1, 1)
        self.inputLayout.addWidget(self.eventDirectoryNameComboBox, 4, 1)

        # Path browser buttons
        self.browseMediaLocation = QPushButton("...")
        self.browseMediaDestination = QPushButton("...")
        self.inputLayout.addWidget(self.browseMediaLocation, 0, 2)
        self.inputLayout.addWidget(self.browseMediaDestination, 1, 2)

        # Media code drop down
        self.mediaCodeComboBox = QComboBox(self)
        self.inputLayout.addWidget(self.mediaCodeComboBox, 2, 1)

        # Add media code button
        self.addMediaCode = QPushButton("New Code")
        self.inputLayout.addWidget(self.addMediaCode, 2, 2)

        # Calendar
        self.eventCalendar = QDateEdit(self)
        self.eventCalendar.setCalendarPopup(True)
        self.eventCalendar.setDate(QDate().currentDate())
        self.eventCalendar.setMaximumDate(QDate.currentDate())
        self.eventCalendar.setDisplayFormat("yyyy-MM-dd")
        self.eventCalendar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        popUpCalendar = self.eventCalendar.calendarWidget()
        popUpCalendar.setGridVisible(True)
        self.inputLayout.addWidget(self.eventCalendar, 3, 1)

        return self.inputLayout

# Must be used in grid layout
class MediaLayout(QWidget):
    # Gets executed upon creating an instance of the class
    def __init__(self):
        super().__init__()
        self.mediaViewerLayout = QGridLayout()
        self.setLayout(self.mediaViewerLayout)
        self.addContents()
        self.mediaViewerLayout.setColumnStretch(0, 3)
        self.mediaViewerLayout.setColumnStretch(1, 7)
    
    def addContents(self):
        # List of media found
        self.mediaList = QListWidget()
        self.mediaViewerLayout.addWidget(self.mediaList, 0, 0)

        # Preview of media selected in the list
        self.mediaBoxFrame = QFrame()
        self.mediaBoxFrame.setFrameShape(QFrame.Shape.Box)
        self.mediaBoxFrame.setLineWidth(2)

        # Layout container for the previewed media
        self.mediaBox = QVBoxLayout()
        self.mediaBox.setContentsMargins(15, 15, 15, 15)

        self.mediaViewerLayout.addWidget(self.mediaBoxFrame, 0, 1)
        self.mediaViewerLayout.setColumnStretch(0, 4)
        self.mediaViewerLayout.setColumnStretch(1, 6)
        self.mediaViewerLayout.setHorizontalSpacing(20)

        return self.mediaViewerLayout

class ActionButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.buttonsLayout = QGridLayout()
        self.buttonsLayout.setColumnStretch(0, 1)
        self.buttonsLayout.setColumnStretch(1, 1)
        self.buttonsLayout.setColumnStretch(2, 8)
        self.buttonsLayout.setHorizontalSpacing(30)
        self.setLayout(self.buttonsLayout)

        # Rename Button
        self.renameButton = self.createRenameButton()

        # Show Button
        self.showButton = self.createShowButton()

        # Adding the buttons to the buttons layout
        self.buttonsLayout.addWidget(self.renameButton, 0, 0)
        self.buttonsLayout.addWidget(self.showButton, 0, 1)
    
    def createRenameButton(self):
        return QPushButton("RENAME\nMEDIA")
    
    def createShowButton(self):
        return QPushButton("SHOW MEDIA\nDESTINATION")