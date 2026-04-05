import moderngl
import glfw
from dataclasses import dataclass


class GLctx:
    ctx=None
    LABEL = 'GLctx'
    
    @classmethod
    def get(self):
        if not self.ctx:
            self.ctx = moderngl.create_context(standalone=True)
        return self.ctx
    
