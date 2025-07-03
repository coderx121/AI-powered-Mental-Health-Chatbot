from PyQt5.QtWidgets import QApplication, QFrame, QSizePolicy, QMainWindow, QLabel, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
AssistantName = "Melo AI"
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"
is_chatbot_stopped = False  # Global flag to track if chatbot is stopped

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
      new_query = Query.lower().strip()
      query_words = new_query.split()
      question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

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
      with open(rf"{TempDirPath}\Mic.data", "w", encoding="utf-8") as file:
            file.write(Command)

def GetMicrophoneStatus():
      with open(rf"{TempDirPath}\Mic.data", "r", encoding="utf-8") as file:
            Status = file.read()
      return Status

def SetAssistantStatus(Status):
      with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
            file.write(Status)

def GetAssistantStatus():
      with open(rf"{TempDirPath}\Status.data", "r", encoding="utf-8") as file:
            Status = file.read()
      return Status

def MicButtonInitialized():
      SetMicrophoneStatus("False")

def MicButtonClosed():
      SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
      Path = rf"{GraphicsDirPath}\{Filename}"
      return Path

def TempDirectoryPath(Filename):
      Path = rf"{TempDirPath}\{Filename}"
      return Path

def ShowTextToScreen(Text):
      with open(rf"{TempDirPath}\Responses.data", "w", encoding="utf-8") as file:
            file.write(Text)

class ChatSection(QWidget):
      def __init__(self):
            super(ChatSection, self).__init__()
            
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)  # Adjusted margins
            layout.setSpacing(10)  # Adjusted spacing

            self.chat_text_edit = QTextEdit()
            self.chat_text_edit.setReadOnly(True)
            self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
            self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
            layout.addWidget(self.chat_text_edit)

            # Add placeholder text to confirm display
            self.addMessage(message="Welcome to Melo AI Chat! Speak to start.", color='White')

            self.setStyleSheet("background-color: black;")
            layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
            layout.setStretch(1, 1)

            self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            text_color = QColor(Qt.blue)
            text_color_text = QTextCharFormat()
            text_color_text.setForeground(text_color)
            self.chat_text_edit.setCurrentCharFormat(text_color_text)

            # GIF label widget
            self.gif_label = QLabel()
            self.gif_label.setStyleSheet("border: none;")
            movie = QMovie(GraphicsDirectoryPath("melo.gif"))
            max_gif_size = QSize(480, 480)
            movie.setScaledSize(max_gif_size)
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.gif_label.setMovie(movie)
            movie.start()
            layout.addWidget(self.gif_label)

            # Label widget
            self.label = QLabel()
            self.label.setStyleSheet("border: none; color: white; font-size: 16px;")
            layout.addWidget(self.label)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.LoadMessages)
            self.timer.timeout.connect(self.SpeechRecogText)
            self.timer.start(5)

            self.icon_label = QLabel(self)
            self.toggled = False

            self.chat_text_edit.viewport().installEventFilter(self)

            self.setStyleSheet("""
                  QScrollBar:vertical {
                  border: none;
                  background: black;
                  width: 10px;
                  margin: 0px 0px 0px 0px;
                 }

                  QScrollBar::handle:vertical {
                  background: white;
                  min-height: 20px;
                 }

                  QScrollBar::add-line:vertical {
                  background: black;
                  height: 10px;
                  subcontrol-position: bottom;
                  subcontrol-origin: margin;
                 }

                  QScrollBar::sub-line:vertical {
                  background: black;
                  height: 10px;
                  subcontrol-position: top;
                  subcontrol-origin: margin;
                 }

                  QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                  border: none;
                  background: none;
                  color: none;
                 }

                  QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                  background: none;
                 }
            """)    

      def LoadMessages(self):
            global old_chat_message, is_chatbot_stopped
            if is_chatbot_stopped:
                  return  # Skip loading new messages if chatbot is stopped
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                  messages = file.read()
                  if None == messages:
                        pass
                  elif len(messages) <= 1:
                        pass
                  elif str(old_chat_message) == str(messages):
                        pass
                  else:
                        self.addMessage(message=messages, color='White')
                        old_chat_message = messages                      

      def SpeechRecogText(self):
            global is_chatbot_stopped
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                  messages = file.read()
                  self.label.setText(messages)
                  # Check if "stop" is in the speech input
                  if messages.strip().lower() == "stop":
                        is_chatbot_stopped = True
                        self.addMessage(message="Chatbot stopped. Speak a new command to resume.", color='Yellow')
                  elif messages.strip():  # Non-empty input that isn't "stop"
                        is_chatbot_stopped = False

      def load_icon(self, path, width=60, height=60):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

      def toggle_icon(self, event=None):
           if self.toggled:
                 self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
                 MicButtonInitialized()
           else:
                 self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
                 MicButtonClosed()
           self.toggled = not self.toggled

      def addMessage(self, message, color):
            cursor = self.chat_text_edit.textCursor()
            format = QTextCharFormat()
            formatm = QTextBlockFormat()
            formatm.setTopMargin(10)
            formatm.setLeftMargin(10)
            format.setForeground(QColor(color))
            cursor.setCharFormat(format)
            cursor.setBlockFormat(formatm)
            cursor.insertText(message + "\n")
            self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
      def __init__(self, parent=None):
            super().__init__(parent)
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()

            # Main layout with no margins
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # GIF label to cover full screen
            self.gif_label = QLabel(self)
            self.gif_label.setStyleSheet("border: none;")
            movie = QMovie(GraphicsDirectoryPath('melo.gif'))
            self.gif_label.setMovie(movie)
            movie.setScaledSize(QSize(screen_width, screen_height))
            self.gif_label.setAlignment(Qt.AlignCenter)
            self.gif_label.setScaledContents(True)
            movie.start()
            self.gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.gif_label.setGeometry(0, 0, screen_width, screen_height)

            # Overlay widget for microphone and status label
            overlay_widget = QWidget(self)
            overlay_widget.setStyleSheet("background: transparent;")
            overlay_layout = QVBoxLayout(overlay_widget)
            overlay_layout.setContentsMargins(0, 0, 0, 150)
            overlay_layout.setSpacing(10)

            # Status label
            self.label = QLabel("")
            self.label.setStyleSheet("color: white; font-size: 16px; background: transparent;")
            overlay_layout.addStretch()
            overlay_layout.addWidget(self.label, alignment=Qt.AlignCenter)

            # Microphone icon
            self.icon_label = QLabel()
            pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
            new_pixmap = pixmap.scaled(60, 60)
            self.icon_label.setPixmap(new_pixmap)
            self.icon_label.setFixedSize(150, 150)
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.toggled = True
            self.toggle_icon()
            self.icon_label.mousePressEvent = self.toggle_icon
            overlay_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

            # Add widgets to main layout
            main_layout.addWidget(self.gif_label)
            main_layout.addWidget(overlay_widget)

            self.setLayout(main_layout)
            self.setFixedSize(screen_width, screen_height)
            self.setStyleSheet("background-color: black;")

            # Timer for status updates
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.SpeechRecogText)
            self.timer.start(5)

      def SpeechRecogText(self):
            global is_chatbot_stopped
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                  messages = file.read()
                  self.label.setText(messages)
                  # Check if "stop" is in the speech input
                  if messages.strip().lower() == "stop":
                        is_chatbot_stopped = True
                  elif messages.strip():  # Non-empty input that isn't "stop"
                        is_chatbot_stopped = False

      def load_icon(self, path, width=60, height=60):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

      def toggle_icon(self, event=None):
            if self.toggled:
                  self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
                  MicButtonInitialized()
            else:
                  self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
                  MicButtonClosed()
            self.toggled = not self.toggled

class MessageScreen(QWidget):
      def __init__(self, parent=None):
            super().__init__(parent)
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Placeholder label for debugging
            placeholder_label = QLabel("Chat Screen")
            placeholder_label.setStyleSheet("color: white; font-size: 20px;")
            layout.addWidget(placeholder_label, alignment=Qt.AlignTop)

            chat_section = ChatSection()
            layout.addWidget(chat_section)

            self.setLayout(layout)
            self.setStyleSheet("background-color: black;")
            self.setFixedHeight(screen_height)
            self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
      def __init__(self, parent, stacked_widget):
            super().__init__(parent)
            self.stacked_widget = stacked_widget
            self.current_screen = None
            self.init_UI()

      def init_UI(self):
            self.setFixedHeight(50)
            layout = QHBoxLayout(self)
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(5)

            # Title label
            title_label = QLabel(" Melo AI ")
            title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")
            layout.addWidget(title_label)

            # Line frame
            line_frame = QFrame()
            line_frame.setFixedHeight(1)
            line_frame.setFrameShape(QFrame.HLine)
            line_frame.setFrameShadow(QFrame.Sunken)
            line_frame.setStyleSheet("border-color: black;")
            layout.addWidget(line_frame)

            # Add stretch to push buttons to the right
            layout.addStretch()

            # Home button
            home_button = QPushButton()
            home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
            home_button.setIcon(home_icon)
            home_button.setText(" Home")
            home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")
            home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
            layout.addWidget(home_button)

            # Chat button
            message_button = QPushButton()
            message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
            message_button.setIcon(message_icon)
            message_button.setText(" Chat")
            message_button.setStyleSheet("height:40px; line-height:40px; background-color: white; color: black")
            message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
            layout.addWidget(message_button)

            # Minimize button
            minimize_button = QPushButton()
            minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
            minimize_button.setIcon(minimize_icon)
            minimize_button.setStyleSheet("background-color:white")
            minimize_button.clicked.connect(self.minimizeWindow)
            layout.addWidget(minimize_button)

            # Maximize button
            self.maximize_button = QPushButton()
            self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
            self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
            self.maximize_button.setIcon(self.maximize_icon)
            self.maximize_button.setFlat(True)
            self.maximize_button.setStyleSheet("background-color:white")
            self.maximize_button.clicked.connect(self.maximizeWindow)
            layout.addWidget(self.maximize_button)

            # Close button
            close_button = QPushButton()
            close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
            close_button.setIcon(close_icon)
            close_button.setStyleSheet("background-color:white")
            close_button.clicked.connect(self.closeWindow)
            layout.addWidget(close_button)

            self.draggable = True
            self.offset = None

      def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.white)
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

      def mousePressEvent(self, event):
            if self.draggable:
                self.offset = event.pos()

      def mouseMoveEvent(self, event):
            if self.draggable and self.offset:
                  new_pos = event.globalPos() - self.offset
                  self.parent().move(new_pos)

      def showMessageScreen(self):
            if self.current_screen is not None:
                  self.current_screen.hide()
            message_screen = MessageScreen(self)
            layout = self.parent().layout()
            if layout is not None:
                  layout.addWidget(message_screen)
            self.current_screen = message_screen

      def showInitialScreen(self):
            if self.current_screen is not None:
                  self.current_screen.hide()
            initial_screen = InitialScreen(self)
            layout = self.parent().layout()
            if layout is not None:
                  layout.addWidget(initial_screen)
            self.current_screen = initial_screen

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
        
            initial_screen = InitialScreen()
            message_screen = MessageScreen()
        
            stacked_widget.addWidget(initial_screen)
            stacked_widget.addWidget(message_screen)
        
            self.setGeometry(0, 0, screen_width, screen_height)
            self.setStyleSheet("background-color: black;")
        
            top_bar = CustomTopBar(self, stacked_widget)
            self.setMenuWidget(top_bar)
        
            self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
      app = QApplication(sys.argv)
      window = MainWindow()
      window.show()
      sys.exit(app.exec_())

if __name__ == "__main__":
      GraphicalUserInterface()