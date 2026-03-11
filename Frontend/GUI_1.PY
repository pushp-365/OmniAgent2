import sys
import os
from dotenv import dotenv_values

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import (
    QIcon, QPainter, QMovie, QColor,
    QTextCharFormat, QFont, QPixmap, QTextBlockFormat
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QFrame, QSizePolicy, QStackedWidget
)

# ────────────────────────────────────────────────────────────────
#  Globals & helpers  
# ────────────────────────────────────────────────────────────────
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join(line.strip() for line in lines if line.strip())


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "who", "where", "when", "why",
        "which", "whose", "whom", "can you", "what's", "where's", "how's"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)


def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        return file.read()


def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)


def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        return file.read()


def MicButtonInitialed():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'


def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'


def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
        file.write(Text)

# ────────────────────────────────────────────────────────────────
#  Chat section
# ────────────────────────────────────────────────────────────────
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-8)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding,
                                       QSizePolicy.Policy.Expanding))

        # default text colour
        fmt = QTextCharFormat()
        fmt.setForeground(QColor('blue'))
        self.chat_text_edit.setCurrentCharFormat(fmt)

        # animated GIF
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        # status label
        self.label = QLabel("")
        self.label.setStyleSheet(
            "color: white; font-size:16px; margin-right: 195px; border: none; margin-top:-30px;"
        )
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.setLayout(layout)

    # -------------------- helpers --------------------
    def loadMessages(self):
        global old_chat_message
        with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()

        if not messages.strip():
            return
        if messages == old_chat_message:
            return

        self.addMessage(message=messages, color='white')
        old_chat_message = messages

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            self.label.setText(file.read())

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path).scaled(width, height)
        self.icon_lable.setPixmap(pixmap)      # icon_lable exists in InitialScreen

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Voice.jpg'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.jpg'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        block_fmt = QTextBlockFormat()
        block_fmt.setTopMargin(10)
        block_fmt.setLeftMargin(10)

        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.setBlockFormat(block_fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)




# ────────────────────────────────────────────────────────────────
#  Initial & message screens
# ────────────────────────────────────────────────────────────────
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # main GIF
        gif_lable = QLabel()
        movie = QMovie(GraphicsDirectoryPath('jarvis.gif'))
        movie.setScaledSize(QSize(screen_width, int(screen_width / 16 * 9)))
        gif_lable.setMovie(movie)
        gif_lable.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_lable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # mic icon
        self.icon_lable = QLabel()
        self.icon_lable.setFixedSize(150, 150)
        self.icon_lable.setAlignment(Qt.AlignCenter)
        self.load_icon(GraphicsDirectoryPath('Mic_on.jpg'), 60, 60)

        self.toggled = True
        self.icon_lable.mousePressEvent = self.toggle_icon

        # status label
        self.lable = QLabel("")
        self.lable.setStyleSheet("color:white ; font-size:16px ; margin-bottom:0;")

        # assemble
        content_layout.addWidget(gif_lable, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.lable, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_lable, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    # --------------------
    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            self.lable.setText(file.read())

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path).scaled(width, height)
        self.icon_lable.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('mic_off.jpg'), 60, 60)
            MicButtonClosed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic_on.jpg'), 60, 60)
            MicButtonInitialed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))        # placeholder
        layout.addWidget(ChatSection())

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
# ────────────────────────────────────────────────────────────────
#  Custom title bar
# ────────────────────────────────────────────────────────────────
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.current_screen = None
        self.stacked_widget = stacked_widget
        self.offset = None
        self.draggable = True
        self.initUI()

    # --------------------
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        # buttons
        home_button = QPushButton(" Home")
        home_button.setStyleSheet("height:40px; background-color:white; color:black")
        home_button.setIcon(QIcon(GraphicsDirectoryPath("home.jpg")))

        message_button = QPushButton(" Chats")
        message_button.setStyleSheet("height:40px; background-color:white; color:black")
        message_button.setIcon(QIcon(GraphicsDirectoryPath("chats.jpg")))

        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('minimize2.jpg')))
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('maximize.jpg'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('minimize2.jpg'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath('close.jpg')))
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        # title
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        # layout
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        # events
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

    # -------------------- window controls --------------------
    def paintEvent(self, event):
        QPainter(self).fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    # -------------------- drag --------------------
    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.parent().pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset and event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.offset)

# ────────────────────────────────────────────────────────────────
#  Main window & bootstrap
# ────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())

        self.setCentralWidget(stacked_widget)
        self.setMenuWidget(CustomTopBar(self, stacked_widget))

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()

