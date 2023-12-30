import json
import xml.dom.minidom
from xml.parsers.expat import ExpatError
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QSplitter
from PyQt5.QtGui import QTextOption, QDragEnterEvent, QDropEvent, QFont, QTextCursor
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerJSON, QsciLexerXML


class DragDropTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().text().replace("file://", "")
        with open(file_path, 'r') as file:
            self.setText(file.read())

def shorten_and_sort_logs():
    log_lines = input.toPlainText().split('\n')
    for i in range(len(log_lines)):
        match = re.search(r'.*\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\].*?\[(INFO|ERROR)\](.*)', log_lines[i])
        if match:
            log_lines[i] = f'[{match.group(1)}] [{match.group(2)}]{match.group(3)}'
    log_lines.sort()
    input.setPlainText('\n'.join(log_lines))

json_lexer = QsciLexerJSON()
xml_lexer = QsciLexerXML()
font = QFont()
font.setFamily('Courier New')
font.setFixedPitch(True)
font.setPointSize(12)
xml_lexer.setFont(font)
json_lexer.setFont(font)

def pretty_print_line():
    cursor = input.textCursor()
    cursor.movePosition(QTextCursor.StartOfLine)
    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    log_line = cursor.selectedText()
    
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
            pretty_xml = xml_obj.toprettyxml(indent='       ')
            output.setText(pretty_xml)
            output.setLexer(xml_lexer)
            return
        except ExpatError:
            pass

    # If no JSON or XML was found, clear the output
    output.clear()

def import_text():
    file_name, _ = QFileDialog.getOpenFileName(main_window, "Open Text File", "", "Text Files (*.txt)")
    if file_name:
        with open(file_name, 'r') as file:
            input.setPlainText(file.read())

app = QApplication([])

main_window = QWidget()
main_window.showMaximized()

button_layout = QHBoxLayout()
button_layout.setAlignment(Qt.AlignLeft)

import_button = QPushButton("Import", main_window)
import_button.clicked.connect(import_text)
import_button.setMaximumWidth(import_button.sizeHint().width())
button_layout.addWidget(import_button)

shorten_and_sort_button = QPushButton("Shorten and Sort", main_window)
shorten_and_sort_button.clicked.connect(shorten_and_sort_logs)
shorten_and_sort_button.setMaximumWidth(shorten_and_sort_button.sizeHint().width())
button_layout.addWidget(shorten_and_sort_button)

button_layout.addStretch(1)

splitter = QSplitter(Qt.Horizontal, main_window)
splitter.setStyleSheet("""
    QSplitter::handle {
        background: #ACACAC;
    }
""")

input = DragDropTextEdit(main_window)
input.setWordWrapMode(QTextOption.NoWrap)
input.cursorPositionChanged.connect(pretty_print_line)
input.setFont(QFont('Courier New'))
splitter.addWidget(input)

output = QsciScintilla(main_window)
output.setWrapMode(QsciScintilla.WrapNone)
output.setFont(QFont('Courier New'))
splitter.addWidget(output)

main_layout = QVBoxLayout(main_window)
main_layout.addLayout(button_layout)
main_layout.addWidget(splitter)
input_output_layout = QHBoxLayout()
main_layout.addLayout(input_output_layout)

app.exec_()
