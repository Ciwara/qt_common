#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout

# from ..cstatic import CConstants
from .common import FDialog, FWidget


class HTMLView(FDialog, FWidget):
    def __init__(self, html_content, parent=None):
        super(HTMLView, self).__init__(parent)

        layout = QVBoxLayout(self)

        # Assuming you have an HTML content passed to the view
        web_view = QWebEngineView()
        web_view.setHtml(html_content)

        layout.addWidget(web_view)


# class LoginWidget(FDialog, FWidget):
#     title_page = "Identification"

#     def __init__(self, parent=None, hibernate=False, *args, **kwargs):
#         QDialog.__init__(self, parent=parent, *args, **kwargs)
#         self.hibernate = hibernate

#         self.setWindowFlags(Qt.FramelessWindowHint)
#         self.title = FormLabel(
#             "<h4>{app_name}</h4><stromg>Ver: {version}</stromg>".format(
#                 app_name=CConstants.APP_NAME, version=CConstants.APP_VERSION
#             )
#         )
#         self.title.setStyleSheet(
#             """ background: url({}) #DAF7A6;
#                 border-radius: 14px 14px 8px 8px; border: 10px double #128a76 ;
#                 width: 100%; height: auto; padding: 1em;
#                 font: 8pt 'Arial';""".format(
#                 CConstants.APP_LOGO
#             )
#         )
#         vbox = QHBoxLayout()

#         self.loginUserGroupBox()
#         vbox.addWidget(self.title)
#         vbox.addWidget(self.topLeftGroupBox)
#         # set focus to username field
#         self.setFocusProxy(self.password_field)
#         self.setLayout(vbox)
