# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gl_main_ui.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

from glsl_studio.ui.util.HotCombo import HotCombo

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(673, 556)
        self.verticalLayout_8 = QVBoxLayout(Form)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.Tabs = QTabWidget(Form)
        self.Tabs.setObjectName(u"Tabs")
        self.Tab_2D = QWidget()
        self.Tab_2D.setObjectName(u"Tab_2D")
        self.horizontalLayout_2 = QHBoxLayout(self.Tab_2D)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.VL_Tools = QVBoxLayout()
        self.VL_Tools.setObjectName(u"VL_Tools")
        self.GBL_CP = QGroupBox(self.Tab_2D)
        self.GBL_CP.setObjectName(u"GBL_CP")
        self.verticalLayout_12 = QVBoxLayout(self.GBL_CP)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.CoB_2d_Target_IMG = HotCombo(self.GBL_CP)
        self.CoB_2d_Target_IMG.setObjectName(u"CoB_2d_Target_IMG")

        self.verticalLayout_12.addWidget(self.CoB_2d_Target_IMG)

        self.Btn_2d_Exc = QPushButton(self.GBL_CP)
        self.Btn_2d_Exc.setObjectName(u"Btn_2d_Exc")

        self.verticalLayout_12.addWidget(self.Btn_2d_Exc)


        self.VL_Tools.addWidget(self.GBL_CP)

        self.BGL_Props = QGroupBox(self.Tab_2D)
        self.BGL_Props.setObjectName(u"BGL_Props")
        self.verticalLayout_13 = QVBoxLayout(self.BGL_Props)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.SA_2d_PropArea = QScrollArea(self.BGL_Props)
        self.SA_2d_PropArea.setObjectName(u"SA_2d_PropArea")
        self.SA_2d_PropArea.setWidgetResizable(True)
        self.VSAL_2d_prop_content = QWidget()
        self.VSAL_2d_prop_content.setObjectName(u"VSAL_2d_prop_content")
        self.VSAL_2d_prop_content.setGeometry(QRect(0, 0, 289, 326))
        self.VL_2d_props_content = QVBoxLayout(self.VSAL_2d_prop_content)
        self.VL_2d_props_content.setObjectName(u"VL_2d_props_content")
        self.SA_2d_PropArea.setWidget(self.VSAL_2d_prop_content)

        self.verticalLayout_13.addWidget(self.SA_2d_PropArea)


        self.VL_Tools.addWidget(self.BGL_Props)


        self.horizontalLayout_2.addLayout(self.VL_Tools)

        self.VL_2d_MainStack = QVBoxLayout()
        self.VL_2d_MainStack.setObjectName(u"VL_2d_MainStack")
        self.GB_LayersStack = QGroupBox(self.Tab_2D)
        self.GB_LayersStack.setObjectName(u"GB_LayersStack")
        self.verticalLayout_2 = QVBoxLayout(self.GB_LayersStack)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.CoB_2d_stack_remove = HotCombo(self.GB_LayersStack)
        self.CoB_2d_stack_remove.setObjectName(u"CoB_2d_stack_remove")

        self.verticalLayout_2.addWidget(self.CoB_2d_stack_remove)

        self.CoB_2d_stack_add = HotCombo(self.GB_LayersStack)
        self.CoB_2d_stack_add.setObjectName(u"CoB_2d_stack_add")

        self.verticalLayout_2.addWidget(self.CoB_2d_stack_add)

        self.VSA_2d_StackArea = QScrollArea(self.GB_LayersStack)
        self.VSA_2d_StackArea.setObjectName(u"VSA_2d_StackArea")
        self.VSA_2d_StackArea.setWidgetResizable(True)
        self.VL_2d_Stack_Area_Content = QWidget()
        self.VL_2d_Stack_Area_Content.setObjectName(u"VL_2d_Stack_Area_Content")
        self.VL_2d_Stack_Area_Content.setGeometry(QRect(0, 0, 288, 365))
        self.VL_2D_stack_content = QVBoxLayout(self.VL_2d_Stack_Area_Content)
        self.VL_2D_stack_content.setObjectName(u"VL_2D_stack_content")
        self.VS_2D_VSA_stacker = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.VL_2D_stack_content.addItem(self.VS_2D_VSA_stacker)

        self.VSA_2d_StackArea.setWidget(self.VL_2d_Stack_Area_Content)

        self.verticalLayout_2.addWidget(self.VSA_2d_StackArea)


        self.VL_2d_MainStack.addWidget(self.GB_LayersStack)


        self.horizontalLayout_2.addLayout(self.VL_2d_MainStack)

        self.Tabs.addTab(self.Tab_2D, "")
        self.Tab_3D = QWidget()
        self.Tab_3D.setObjectName(u"Tab_3D")
        self.horizontalLayout = QHBoxLayout(self.Tab_3D)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Tabs.addTab(self.Tab_3D, "")

        self.verticalLayout_8.addWidget(self.Tabs)

        self.L_IO = QHBoxLayout()
        self.L_IO.setObjectName(u"L_IO")
        self.Btn_Export = QPushButton(Form)
        self.Btn_Export.setObjectName(u"Btn_Export")

        self.L_IO.addWidget(self.Btn_Export)

        self.Btn_Import = QPushButton(Form)
        self.Btn_Import.setObjectName(u"Btn_Import")

        self.L_IO.addWidget(self.Btn_Import)


        self.verticalLayout_8.addLayout(self.L_IO)


        self.retranslateUi(Form)

        self.Tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.GBL_CP.setTitle(QCoreApplication.translate("Form", u"Observer Panel", None))
        self.Btn_2d_Exc.setText(QCoreApplication.translate("Form", u"Execute", None))
        self.BGL_Props.setTitle(QCoreApplication.translate("Form", u"Inspector Panel", None))
        self.GB_LayersStack.setTitle(QCoreApplication.translate("Form", u"Layers Panel", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.Tab_2D), QCoreApplication.translate("Form", u"2D", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.Tab_3D), QCoreApplication.translate("Form", u"3D", None))
        self.Btn_Export.setText(QCoreApplication.translate("Form", u"Export", None))
        self.Btn_Import.setText(QCoreApplication.translate("Form", u"Import", None))
    # retranslateUi

