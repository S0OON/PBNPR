import moderngl
import glfw
from dataclasses import dataclass


class GLctx:
    ctx=None
    LABEL = 'GLctx'
    @classmethod
    def INIT(self):
        # --- Context Initialization with GLFW Hidden Window ---
        try:
            # 1. Primary: Try to hook into Blender's existing UI window
            self.ctx = moderngl.create_context()
            print(f"[{self.LABEL}] Hooked into Blender's existing OpenGL Context.")
            
        except Exception:
            print(f"[{self.LABEL}] No active context. Attempting GLFW hidden window...")
            try:
                # 2. Fallback: The Hidden Window Hack
                if not glfw.init():
                    raise Exception("Failed to initialize GLFW.")
                
                # Tell GLFW not to actually show the window on the monitor
                glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
                
                # Create a tiny 100x100 dummy window in the background
                self.glfw_window = glfw.create_window(100, 100, "Dummy", None, None)
                if not self.glfw_window:
                    glfw.terminate()
                    raise Exception("Failed to create hidden GLFW window.")
                
                # Make this hidden window the "current" OpenGL target
                glfw.make_context_current(self.glfw_window)
                
                # Now ModernGL will happily hook into the WGL context GLFW just built!
                self.ctx = moderngl.create_context()
                print(f"[{self.LABEL}] Hooked into Hidden GLFW Window via WGL.")
                
            except Exception as e:
                print(f"[{self.LABEL}] GLFW Fallback failed: {e}. Forcing EGL...")
                # 3. Last Resort: Force EGL offscreen rendering
                self.ctx = moderngl.create_context(standalone=True, backend='egl')
    @classmethod
    def get(self):
        if not self.ctx:
            self.INIT()
        return self.ctx
    
