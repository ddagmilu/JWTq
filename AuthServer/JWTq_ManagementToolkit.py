import sys
import random
import string
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QCoreApplication, QUrl, QProcess
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os

from generate_topology import LoadTopologyHTML, TopologyCreat  # Import your topology functions

os.environ["QT_QPA_PLATFORMTHEME"] = "gtk3"
os.environ["QT_STYLE_OVERRIDE"] = "Fusion"

class JWTqApp(QMainWindow):
    def __init__(self):
        super(JWTqApp, self).__init__()
        loadUi("JWTq_GUI.ui", self)

        # Ensure these names match the names in your .ui file
        try:
            self.tokenlist_button_search.clicked.connect(self.search_tokens)
            self.tokenlist_button_refresh.clicked.connect(self.refresh_tokens)
            self.adddevice_button_add.clicked.connect(self.add_token)
            self.adddevice_checkbox_publishright.stateChanged.connect(self.toggle_publish_right)
            self.tokenlist_table.itemClicked.connect(self.load_token_info)
        except AttributeError as e:
            QMessageBox.critical(self, "UI Error", f"Error connecting signals: {e}")
            sys.exit(1)

        # Make the code field read-only
        self.tokeninfo_lineedit_code.setReadOnly(True)

        # Load the topology HTML file in QWebEngineView
        self.tokeninformation_webengine_view = self.findChild(QWebEngineView, 'tokeninformation_webengine_view')

        # Initially refresh the token list
        self.refresh_tokens()

    def fetch_tokens(self):
        try:
            response = requests.get("http://127.0.0.1:5000/token/list")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            QMessageBox.critical(self, "API Error", f"Error fetching tokens: {e}")
            return []

    def refresh_tokens(self):
        tokens = self.fetch_tokens()
        self.tokenlist_table.setRowCount(0)  # Clear existing rows
        for token in tokens:
            self.add_token_to_table(token)

        self.update_token_capacity_progress_bar(len(tokens))

    def add_token_to_table(self, token):
        row_position = self.tokenlist_table.rowCount()
        self.tokenlist_table.insertRow(row_position)
        self.tokenlist_table.setItem(row_position, 0, QTableWidgetItem(token['code']))
        self.tokenlist_table.setItem(row_position, 1, QTableWidgetItem(token['role']))
        self.tokenlist_table.setItem(row_position, 2, QTableWidgetItem(str(token['publish_right'])))

    def search_tokens(self):
        search_text = self.tokenlist_bar_search.text().lower()  # Get text from QLineEdit
        for row in range(self.tokenlist_table.rowCount()):
            item_code = self.tokenlist_table.item(row, 0).text().lower()
            item_role = self.tokenlist_table.item(row, 1).text().lower()
            if search_text in item_code or search_text in item_role:
                self.tokenlist_table.setRowHidden(row, False)
            else:
                self.tokenlist_table.setRowHidden(row, True)

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            response = requests.get(f'http://127.0.0.1:5000/token/check_code/{code}')
            if not response.json().get('exists'):
                return code

    def toggle_publish_right(self, state):
        self.adddevice_textline_publish.setEnabled(state == 2)  # 2 is the state when checkbox is checked

    def add_token(self):
        try:
            code = self.generate_unique_code()
            self.adddevice_lineedit_code.setText(code)
            role = self.adddevice_combobox_role.currentText() + ':' + self.adddevice_lineedit_role.text()
            publish_right = self.adddevice_checkbox_publishright.isChecked()
            subscribe_topics = self.adddevice_textline_subscribe.toPlainText().splitlines()
            publish_topics = self.adddevice_textline_publish.toPlainText().splitlines() if publish_right else []

            token_data = {
                'code': code,
                'role': role,
                'messages_class': 'default_class',  # You can update this as needed
                'publish_right': publish_right,
                'sub_topic': subscribe_topics,
                'pub_topic': publish_topics
            }

            response = requests.post('http://127.0.0.1:5000/token/issue', json=token_data)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Token added successfully')
                self.refresh_tokens()  # Refresh token list after adding new token
            else:
                QMessageBox.critical(self, 'Error', 'Failed to add token')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def update_token_capacity_progress_bar(self, used_tokens_count):
        total_possible_tokens = 62 ** 6
        used_percentage = (used_tokens_count / total_possible_tokens) * 100
        self.tokencapacity_progressBar.setValue(int(used_percentage))

    def load_token_info(self, item):
        row = item.row()
        code = self.tokenlist_table.item(row, 0).text()
        try:
            response = requests.get(f'http://127.0.0.1:5000/token/info/{code}')
            response.raise_for_status()
            token_info = response.json()
            if 'error' in token_info:
                QMessageBox.critical(self, "Error", token_info['error'])
            else:
                self.tokeninfo_lineedit_code.setText(token_info['code'])
                self.tokeninfo_lineedit_role.setText(token_info['role'])
                self.tokeninfo_lineedit_class.setText(token_info['messages_class'])
                self.tokeninfo_checkbox_publishright.setChecked(token_info['publish_right'])

                # Format topics as multi-line strings
                pub_topic_formatted = "\n".join(eval(token_info['pub_topic']))
                sub_topic_formatted = "\n".join(eval(token_info['sub_topic']))

                self.tokeninfo_linetext_publish.setPlainText(pub_topic_formatted)
                self.tokeninfo_linetext_subscribe.setPlainText(sub_topic_formatted)

                # Generate the topology HTML file based on token info
                TopologyCreat(token_info)

                # Load the topology HTML file in QWebEngineView
                LoadTopologyHTML(self.tokeninformation_webengine_view)
        except requests.RequestException as e:
            QMessageBox.critical(self, "API Error", f"Error fetching token info: {e}")

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = JWTqApp()
    window.show()
    sys.exit(app.exec_())
