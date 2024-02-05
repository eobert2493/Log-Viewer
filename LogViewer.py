import json
import xml.dom.minidom
from xml.parsers.expat import ExpatError
import re
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QSplitter, QComboBox, QMessageBox, QLabel, QLineEdit
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QColor, QDragMoveEvent
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla, QsciLexerJSON, QsciLexerXML

class InputScintilla(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the default paper (background) color to white and the default text color to black
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, QsciScintilla.STYLE_DEFAULT, QColor("#ffffff"))
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, QsciScintilla.STYLE_DEFAULT, QColor("#000000"))
        self.SendScintilla(QsciScintilla.SCI_STYLECLEARALL)  # Apply the above settings to all styles
        
        # Enable line highlighting
        self.setCaretLineVisible(True)     
        self.setCaretLineBackgroundColor(QColor("#E8E8E8"))

        # Enable line numbers
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginLineNumbers(0, True)
        
        # Set margins font
        font = QFont('Courier New')
        font.setPointSize(16)
        self.setMarginsFont(font)

        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def focusOutEvent(self, event):
        # Keep caret line visible when editor loses focus
        self.setCaretLineVisible(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            # Handle file drop
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.import_text(file_path)

    def import_text(self, file_path):
        try:
            # Try to read the file as a text file
            with open(file_path, 'r') as file:
                self.setText(file.read())
        except UnicodeDecodeError:
            # If a UnicodeDecodeError is raised, show a message box
            QMessageBox.critical(None, "Error", "Only text files are allowed.")

class OutputScintilla(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the default paper (background) color to white and the default text color to black
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, QsciScintilla.STYLE_DEFAULT, QColor("#ffffff"))
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, QsciScintilla.STYLE_DEFAULT, QColor("#000000"))
        self.SendScintilla(QsciScintilla.SCI_STYLECLEARALL)  # Apply the above settings to all styles

        # Enable line highlighting
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#E8E8E8"))
        
        # Enable line numbers
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginLineNumbers(0, True)
        
        # Enable code folding
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        # Set margins font
        font = QFont('Courier New')
        self.setMarginsFont(font)   
             
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)
        
    def focusInEvent(self, event):
       pass
    
    def focusOutEvent(self, event):
        # Keep caret line visible when editor loses focus
        self.setCaretLineVisible(True)

def shorten_and_sort_logs():
    log_lines = input.text().split('\n')
    regex = regex_input.text()
    for i in range(len(log_lines)):
        # match = re.search(r'.*\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\].*?\[(INFO|ERROR|DEBUG|WARNING)\](.*)', log_lines[i])
        match = re.search(regex, log_lines[i])
        if match:
            log_lines[i] = f'[{match.group(1)}] [{match.group(2)}]{match.group(3)}'
    log_lines.sort()
    input.setText('\n'.join(log_lines))
    input.setCursorPosition(0, 0)

def pretty_print_line():
    json_lexer = QsciLexerJSON()
    xml_lexer = QsciLexerXML()

    # Set the color of the tag style
    font = QFont()
    font.setFamily('Courier New')
    font.setFixedPitch(True)
    font.setPointSize(12)
    json_lexer.setFont(font)
    xml_lexer.setFont(font)
    
    line, _ = input.getCursorPosition()
    log_line = input.text(line)

    # Try to find JSON in the log line
    json_match = re.search(r'\{.*\}', log_line)
    if json_match:
        json_str = json_match.group()
        try:
            json_obj = json.loads(json_str)
            pretty_json = json.dumps(json_obj, indent=4)
            output.setText(pretty_json)
            output.setLexer(json_lexer)

            return
        except json.JSONDecodeError:
            pass

    # Try to find XML in the log line
    xml_match = re.search(r'<.*>', log_line)
    if xml_match:
        xml_str = xml_match.group()
        try:
            xml_obj = xml.dom.minidom.parseString(xml_str)
            pretty_xml = xml_obj.toprettyxml(indent='     ')
            output.setText(pretty_xml)
            output.setLexer(xml_lexer)
            return
        except ExpatError:
            pass

    # If no JSON or XML was found, clear the output
    output.clear()

def import_text_dropdown(file_path):
    try:
        # Try to read the file as a text file
        with open(file_path, 'r') as file:
            input.setText(file.read())
    except UnicodeDecodeError:
        # If a UnicodeDecodeError is raised, show a notification to the user
        QMessageBox.critical(None, "Error", "Only text files are allowed.")

# For import button
def import_text():
    file_name, _ = QFileDialog.getOpenFileName(main_window, "Open Text File", "", "Text Files (*.*)")
    if file_name:
        try:
            # Try to read the file as a text file
            with open(file_name, 'r') as file:
                input.setText(file.read())
        except UnicodeDecodeError:
            # If a UnicodeDecodeError is raised, show a message in the status bar
            QMessageBox.critical(None, "Error", "Only text files are allowed.")
                        
def zoomIn():
    # Increase the zoom level by 1
    input.zoomIn()
    output.zoomIn()

def zoomOut():
    # Decrease the zoom level by 1
    input.zoomOut()
    output.zoomOut()
    
app = QApplication([])

app.setStyle('Fusion')
app.setStyleSheet("""
    * {
        font-family: 'Courier New';
        background-color: #ffffff; /* white */
        color: #000000; /* black */
    }
    QComboBox {
        background-color: #ffffff; /* white */
        color: #000000; /* black */
    }
    QSciScintilla {
        background-color: #ffffff; /* white */
        color: #000000; /* black */
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff; /* white */
        color: #000000; /* black */
    }
""")

main_window = QWidget()
main_window.showMaximized()

# Get the list of files in the downloads directory
downloads_dir = os.path.expanduser('~/Downloads')
files = os.listdir(downloads_dir)

# Get the modification times of the files
mod_times = [os.path.getmtime(os.path.join(downloads_dir, file)) for file in files]

# Sort the files by their modification times in descending order
files = [file for _, file in sorted(zip(mod_times, files), reverse=True)]

# Create a QComboBox
file_combo_box = QComboBox(main_window)
file_combo_box.setMaximumHeight(40)


# Add the files to the QComboBox
max_files = 20
for file in files[:max_files]:
    file_combo_box.addItem(file)

# Connect the currentIndexChanged signal to a method that imports the selected file
file_combo_box.currentIndexChanged.connect(lambda: import_text_dropdown(os.path.join(downloads_dir, file_combo_box.currentText())))


button_layout = QHBoxLayout()
button_layout.setAlignment(Qt.AlignLeft)

import_button = QPushButton("Import", main_window)
import_button.clicked.connect(import_text)
import_button.setMaximumWidth(import_button.sizeHint().width())
button_layout.addWidget(import_button)

shorten_and_sort_button = QPushButton("RegEx && Sort", main_window)
shorten_and_sort_button.clicked.connect(shorten_and_sort_logs)
shorten_and_sort_button.setMaximumWidth(shorten_and_sort_button.sizeHint().width())
button_layout.addWidget(shorten_and_sort_button)

button_layout.addWidget(file_combo_box)

# Create a QPushButton for zooming out
zoom_out_button = QPushButton("-", main_window)
zoom_out_button.setMaximumWidth(30)
zoom_out_button.clicked.connect(zoomOut)
button_layout.addWidget(zoom_out_button)

# Create a QPushButton for zooming in
zoom_in_button = QPushButton("+", main_window)
zoom_in_button.setMaximumWidth(30)
zoom_in_button.clicked.connect(zoomIn)
button_layout.addWidget(zoom_in_button)

# Create a QHBoxLayout for the regex input and its label
regex_layout = QHBoxLayout()

# Create a QLabel for the regex input
regex_label = QLabel("RegEx:")
regex_layout.addWidget(regex_label)

# Create a QLineEdit for the regex input
regex_input = QLineEdit()
regex_input.setText(r'.*\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\].*?\[(INFO|ERROR|DEBUG|WARNING)\](.*)')
regex_layout.addWidget(regex_input)

# Add the regex layout to the button layout
button_layout.addLayout(regex_layout)

button_layout.addSpacing(20)

splitter = QSplitter(Qt.Horizontal, main_window)
splitter.setStyleSheet("""
    QSplitter::handle {
        background: #ACACAC;
    }
""")

input = InputScintilla(main_window)
input.setWrapMode(QsciScintilla.WrapNone)
input.cursorPositionChanged.connect(pretty_print_line)
input.setFont(QFont('Courier New'))
splitter.addWidget(input)

output = OutputScintilla(main_window)
output.setWrapMode(QsciScintilla.WrapNone)
output.setFont(QFont('Courier New'))
splitter.addWidget(output)

main_layout = QVBoxLayout(main_window)
main_layout.addLayout(button_layout)
main_layout.addWidget(splitter)
input_output_layout = QHBoxLayout()
main_layout.addLayout(input_output_layout)

app.exec_()
