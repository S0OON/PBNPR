import sys
sys.path.append(r"E:\soon\projects\PBNPR\code\addons")

import gl_studio
import dearpygui.dearpygui as dpg

if __name__ == '__main__':
    gl_studio.ui.dpg_main.register()
    if dpg.is_dearpygui_running():
        gl_studio.ui.dpg_main.register()