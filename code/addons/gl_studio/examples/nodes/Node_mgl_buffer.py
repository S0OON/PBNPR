import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import moderngl
import numpy as np

class NODE_INTERFACE(BASE_NODE):
    CATEGORY = 'MGL'
    LABEL = 'MGL Buffer'
    
    def __init__(self, parent):
        super().__init__(parent)

        self.I_data = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Data')
        self.I_dynamic = t.NodeSocket(dpg.generate_uuid(), t.BOOL, '<- Dynamic', False)
        
        self.O_buffer = t.NodeSocket(dpg.generate_uuid(), t.OB, 'Buffer ->')  # OB = MGL object
        
        self._vbo = None  # Persistent MGL buffer
        

        
    def on_execute(self):
        ctx = GLctx.get()  # Your singleton context
        
        data = self.I_data.value
        if data is None: return
        
        # Create or resize buffer
        if self._vbo is None or self.I_dynamic.value:
            if self._vbo: self._vbo.release()
            self._vbo = ctx.buffer(data.astype('f4').tobytes())
        else:
            # Orphan + write for dynamic updates (fast)
            self._vbo.orphan(data.astype('f4').tobytes())
            
        self.O_buffer.value = self._vbo