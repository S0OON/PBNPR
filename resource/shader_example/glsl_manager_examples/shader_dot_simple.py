# my_effect.py - Lives in user directory, hot-reloadable
from glsl_manager.gl.shader_pattren import ShaderBase
import numpy as np
import bpy

uOBJm  = "m_world"
uCAMm  = "m_view"
uPROJm = "m_proj"

class MyEffect(ShaderBase):
    # Custom GLSL
    VERT_SRC = """
        #version 330
    """
    
    FRAG_SRC = """
        #version 330
    """
    
    def __init__(self):
        super().__init__()
        # Custom setup if needed
    
    def render_object(self, obj, camera, width, height):
        """High-level render for Blender object"""
        from bpy.mesh_utils import get_mesh_data  # Your util
        
        # Get mesh data from Blender
        positions, normals = get_mesh_data(obj)
        
        # Upload geometry (cached if unchanged)
        self.update_geometry(positions)
        
        # Calculate matrices
        m_world = np.array(obj.matrix_world, dtype=np.float32)
        m_view = np.array(camera.matrix_world.inverted(), dtype=np.float32)
        
        # Render
        pixels = self.render(width, height, uniforms={
            'm_world': m_world,
            'm_view': m_view,
            # ... etc
        })
        
        return pixels