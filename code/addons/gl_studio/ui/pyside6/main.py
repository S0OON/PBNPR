# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2026 S00N

from gl_studio.ui.pyside6 import (
    editor_runtimeInfo,
    editor_nodeGraph,
    internals,
)


def register():
    internals.register()
    editor_nodeGraph.register()
    editor_runtimeInfo.register()


def unregister():
    editor_nodeGraph.unregister()
    editor_runtimeInfo.unregister()
    internals.unregister()


def check_state():
    a = internals.check_state()
    b = editor_nodeGraph.check_state()
    c = editor_runtimeInfo.check_state()
    return all([a, b ,c])


def process_frame():
    internals.process_frame()
    editor_nodeGraph.process_frame()
    editor_runtimeInfo.process_frame()
