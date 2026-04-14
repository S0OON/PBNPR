

import bpy
from gl_studio.ui.pyside6 import main

main.register()
while main.check_state():
    main.process_frame()
main.unregister()