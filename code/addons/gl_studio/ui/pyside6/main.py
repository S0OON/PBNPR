from gl_studio.ui.pyside6 import (
    # editor_general_template_module_file,
    editor_nodeGraph,
    internals,
)


def register():     
    internals.register()
    editor_nodeGraph.register()
    # editor_general_template_module_file.register()


def unregister():
    internals.unregister()
    editor_nodeGraph.unregister()
    # editor_general_template_module_file.unregister()


def check_state():
    a = internals.check_state()
    b = editor_nodeGraph.check_state()
    # c = editor_general_template_module_file.check_state()
    return all([a, b])  # ,c)


def process_frame():
    internals.process_frame()
    editor_nodeGraph.process_frame()
    # editor_general_template_module_file.process_frame()
