# gl_context.py - Initialize once, reuse everywhere
import moderngl
import numpy as np
 
class GLContext:
    """Singleton ModernGL context for rendering"""
    _instance = None
    
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = moderngl.create_context()
            print(f"ModernGL {cls._instance.version_code} initialized")
        return cls._instance
    
    @classmethod
    def release(cls):
        if cls._instance:
            cls._instance.release()
            cls._instance = None


