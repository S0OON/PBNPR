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
        in vec3 in_pos;
        in vec3 in_normal;
        
        uniform mat4 m_world;
        uniform mat4 m_view;
        uniform mat4 m_proj;
        
        out vec3 v_normal;
        
        void main() {
            v_normal = in_normal;
            mat4 mvp = m_proj * m_view * m_world;
            gl_Position = mvp * vec4(in_pos, 1.0);
        }
    """
    
    FRAG_SRC = """
        #version 330
        in vec3 v_normal;
        out vec4 fragColor;
        
        uniform vec3 light_dir;
        uniform vec4 base_color;
        
        void main() {
            float diff = max(dot(normalize(v_normal), normalize(light_dir)), 0.0);
            fragColor = vec4(base_color.rgb * diff, base_color.a);
        }
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