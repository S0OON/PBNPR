# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gl_instance.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

from glsl_studio.ui.util.HotCheckBox import HotCheckBox

class Ui_Frame(object):
    def setupUi(self, Frame):
        if not Frame.objectName():
            Frame.setObjectName(u"Frame")
        Frame.resize(377, 206)
        self.verticalLayout = QVBoxLayout(Frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Frame)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox = HotCheckBox(self.groupBox)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout.addWidget(self.checkBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.Btn_Down = QPushButton(self.groupBox)
        self.Btn_Down.setObjectName(u"Btn_Down")

        self.horizontalLayout.addWidget(self.Btn_Down)

        self.Btn_UP = QPushButton(self.groupBox)
        self.Btn_UP.setObjectName(u"Btn_UP")

        self.horizontalLayout.addWidget(self.Btn_UP)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.Btn_Del = QPushButton(self.groupBox)
        self.Btn_Del.setObjectName(u"Btn_Del")

        self.horizontalLayout.addWidget(self.Btn_Del)


        self.verticalLayout_2.addWidget(self.groupBox)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(Frame)

        QMetaObject.connectSlotsByName(Frame)
    # setupUi

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QCoreApplication.translate("Frame", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("Frame", u"Shader name", None))
        self.checkBox.setText(QCoreApplication.translate("Frame", u"Active", None))
        self.Btn_Down.setText(QCoreApplication.translate("Frame", u"Down", None))
        self.Btn_UP.setText(QCoreApplication.translate("Frame", u"Up", None))
        self.Btn_Del.setText(QCoreApplication.translate("Frame", u"X", None))
    # retranslateUi

