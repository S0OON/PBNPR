from gl_studio.ui.pyside6 import internals
from gl_studio.ui.pyside6 import editor_nodeGraph
from gl_studio.ui.pyside6 import editor_general


def register():
    internals.register()
    editor_nodeGraph.register()
    editor_general.register()

def unregister():
    internals.unregister()
    editor_nodeGraph.unregister()
    editor_general.unregister()

def check_state():
    a = internals.check_state()
    b = editor_nodeGraph.check_state()
    c = editor_general.check_state()
    return a and b and c

def process_frame():
    internals.process_frame()
    editor_nodeGraph.process_frame()
    editor_general.process_frame()