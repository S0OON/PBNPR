import os,bpy,sys
import importlib.util
from PySide6 import QtWidgets, QtCore
from typing import cast
from gl_studio.ui.gl_main_ui_ui import Ui_Form 
from gl_studio.ui.gl_instance_ui import Ui_Frame
from gl_studio.gl import gl_shader2D_template as GLSL_DEFAULT 

global_qt_app = None
global_studio_window = None


# ============================================= 

class GLStudioWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("GL Studio")
        self.IO = {}
        self.ui.Btn_Import.clicked.connect(self.importing)
        
        self.instance = Ui_Frame
        self.stack_items: list[QtWidgets.QWidget] = []

        stack_IMG = self.ui.CoB_2d_Target_IMG
        stack_IMG.label="Target"
        #stack_IMG.PreSuper_Popup = self.IMG_refresh
        #stack_IMG.activated.connect(self.IMG_target_selected)
        self.IMG_refresh()
        stackA = self.ui.CoB_2d_stack_add
        stackA.label="Add"
        stackA.PreSuper_Popup = self.TYPE_refresh
        stackA.activated.connect(self.TYPE_selected_add)
        self.TYPE_refresh()
        stackB = self.ui.CoB_2d_stack_remove
        stackB.label="Remove"
        stackB.PreSuper_Popup = self.TYPE_refresh2
        stackB.activated.connect(self.TYPE_selected_remove)
        self.TYPE_refresh2()
        self.ui.Btn_2d_Exc.clicked.connect(self.activate_instance)

    def closeEvent(self, event):
        event.ignore() 
        self.hide()

    def importing(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Import Shader Module", 
            "", 
            "Python Files (*.py)"
        )
        if not file_path: return

        module_name = os.path.basename(file_path).split('.')[0]
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path) 
            mod = importlib.util.module_from_spec(spec) 
            spec.loader.exec_module(mod)

            self.IO[module_name]=mod

        except Exception as e:
            print(f"FAILED TO IMPORT: {e}")
   
    def IMG_refresh(self):
        stack = self.ui.CoB_2d_Target_IMG 
        stack.clear()
        stack.addItem(stack.label)
        for i, j in bpy.data.images.items():
            stack.addItem(i,j)
    
    def IMG_target_selected(self,index):
        stack = self.ui.CoB_2d_Target_IMG
        txt = stack.itemText(index)
        data = stack.itemData(index)

    def TYPE_refresh(self):
        stack = self.ui.CoB_2d_stack_add 
        stack.clear()
        stack.addItem(stack.label)
        for i, j in self.IO.items():
            stack.addItem(i,j)
   
    def TYPE_refresh2(self):
        stack = self.ui.CoB_2d_stack_remove
        stack.clear()
        stack.addItem(stack.label)
        for i, j in self.IO.items():
            stack.addItem(i,j)

    def TYPE_selected_add(self,index):
        stack = self.ui.CoB_2d_stack_add
        txt = stack.itemText(index)
        data = stack.itemData(index)
        if txt and txt != stack.label:
            self.add_stack_instance(txt,index)
        
    def TYPE_selected_remove(self,index):
        stack = self.ui.CoB_2d_stack_remove
        name = stack.itemText(index)
        self.IO.pop(name, None)
        stack.removeItem(index)
        self.remove_stack_item_by_title(name)

    def remove_stack_item_by_title(self, title: str):
        """Helper that looks for a frame with a matching group box title and removes it."""
        for w in list(self.stack_items):
            gb = w.findChild(QtWidgets.QGroupBox)
            if gb and gb.title() == title:
                self.remove_stack_item(w)
                break

    def add_stack_instance(self, title: str,index:int):
        widget = QtWidgets.QFrame()
        widget.ui = Ui_Frame()
        widget.main = self.ui.CoB_2d_stack_add.itemData(index).MAIN()
        ui = widget.ui
        ui.setupUi(widget)
        ui.groupBox.setTitle(title)

        ui.checkBox.Pre_SuperClick = self.instances_off
        ui.checkBox.clicked.connect(self.Inspect_active_props)
        ui.Btn_UP.clicked.connect(lambda _, w=widget: self.move_stack_item_up(w))
        ui.Btn_Down.clicked.connect(lambda _, w=widget: self.move_stack_item_down(w))
        ui.Btn_Del.clicked.connect(lambda _, w=widget: self.remove_stack_item(w))

        self.stack_items.append(widget)
        layout = self.ui.VL_2D_stack_content
        layout.insertWidget(layout.count() - 1, widget)

    def move_stack_item_up(self, widget: QtWidgets.QWidget):
        try:
            idx = self.stack_items.index(widget)
        except ValueError:
            return
        if idx == 0:
            return  # already at top
        # swap in list
        self.stack_items[idx], self.stack_items[idx - 1] = (
            self.stack_items[idx - 1], self.stack_items[idx]
        )
        # reinsert in layout
        layout = self.ui.VL_2D_stack_content
        layout.removeWidget(widget)
        layout.insertWidget(idx - 1, widget)

    def move_stack_item_down(self, widget: QtWidgets.QWidget):
        """Move a widget one slot lower in the stack area."""
        try:
            idx = self.stack_items.index(widget)
        except ValueError:
            return
        if idx == len(self.stack_items) - 1:
            return  # already at bottom
        # swap in list
        self.stack_items[idx], self.stack_items[idx + 1] = (
            self.stack_items[idx + 1], self.stack_items[idx]
        )
        # reinsert in layout
        layout = self.ui.VL_2D_stack_content
        layout.removeWidget(widget)
        # inserting at idx+1 will place it after the next item
        layout.insertWidget(idx + 1, widget)

    def remove_stack_item(self, widget: QtWidgets.QWidget):
        """Remove a widget from the stack and delete it."""
        if widget in self.stack_items:
            self.stack_items.remove(widget)
        layout = self.ui.VL_2D_stack_content
        layout.removeWidget(widget)
        widget.setParent(None)
        widget.deleteLater()

    def instances_off(self):
        for i in self.stack_items:
            j = cast(Ui_Frame,i.ui)
            j.checkBox.setChecked(False)

    def Inspect_active_props(self):
        target_layout = self.ui.VL_2d_props_content
        self.clear_layout(target_layout)

        for i in self.stack_items:
            j = cast(Ui_Frame,i.ui)
            if j.checkBox.isChecked():
                main = cast(GLSL_DEFAULT.MAIN,i.main)
                main.BUILD_UI(target_layout=target_layout)
                break

        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        target_layout.addItem(spacer)

    def clear_layout(self, layout):
        # (Keep the same clear_layout function from previous step)
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def activate_instance(self):
        for i in self.stack_items:
            i=cast(Ui_Frame,i)
            if i.ui.checkBox.isChecked(): 
                i.main.EXECUTE()
                return

#if __name__ == "__main__":
#    app = QtWidgets.QApplication(sys.argv)
#    win = GLStudioWindow()
#    win.show()
#    while(app.exec()):
#        app.processEvents()
#    sys.exit()