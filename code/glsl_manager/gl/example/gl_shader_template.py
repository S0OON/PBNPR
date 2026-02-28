import bpy
from glsl_manager.gl.util import util_types as t 
from glsl_manager.gl.shader_pattren import ShaderBase,ui_base
import numpy as np
from typing import cast
# this is a simple tringle implementation.

#======================================
class Shader(ShaderBase):
    NAME = "TriangleShader"
    VERT_SRC='''
#version 330\n

in vec2 in_pos;
       
        void main() {
            gl_Position = vec4(in_pos,1.0, 1.0);
        }
'''
    FRAG_SRC='''
#version 330\n
    
    uniform vec4 color;
    
    out vec4 fragColor;
        
        void main() {
            fragColor = color;
        }
'''
    def __init__(self):
        super().__init__()
#======================================
coords = np.array([(-0.5, -0.5), (0.5, -0.5), (0.0, 0.5)], dtype=np.float32)

#======================================
def execute_bake(self,context):
    try:
        self.bake_exec(context)
    except Exception as e:
        print(f"ERROR Failed to bake the shader [{__file__}], report: {e}")

class bpy_ui(ui_base):
    # center
    shader_obj        = Shader()
    Bake              : bpy.props.BoolProperty(default=False,update=execute_bake) # pyright: ignore[reportInvalidTypeForm]
    baking_target_img : bpy.props.PointerProperty(type=bpy.types.Image) # pyright: ignore[reportInvalidTypeForm]
    # peripheral
    color : bpy.props.FloatVectorProperty(name="Color",size=4,subtype="COLOR") # pyright: ignore[reportInvalidTypeForm]
    
    def draw_self_to_panel_canvas(self,canvas:bpy.types.UILayout):
        row = canvas.row(align=True)
        row.prop(self,'Bake',text="",icon='RENDER_RESULT',icon_only=True)
        row.prop(self,'baking_target_img',text="")

        row = canvas.row(align=True)
        row.prop(self,'color',text="")
        
    def bake_exec(self,context):
        ui=self
        if ui.Bake:
            img = cast(bpy.types.Image, ui.baking_target_img)
            if not img: return
            shader = self.shader_obj
            if not shader: 
                ui.report({'ERROR'}, f"Warining, shader object is None at {__file__}") 
                return
            
            shader._uniform(
                color=(ui.color[0], ui.color[1], ui.color[2], ui.color[3]),
            )
            
            VAO = shader.ctx.buffer(coords.tobytes())
            shader.vao = shader.ctx.vertex_array(
                shader.prog,
                [(VAO, '2f', 'in_pos')])
            
            p = shader._exec(img.size[0],img.size[1])

            img.pixels.foreach_set(p.astype(np.float32).reshape(-1) / 255.0)
            self.Bake = False

DESCRIPTION = t.SHADER_INTERP(
    UI     = bpy_ui,
    SHADER = Shader
)


#def exec():
#    """run the example, resault to an image"""
#    s = Shader()
#    res = s.render_object()
#    width, height = 800, 600  # match render_object dimensions
#    img = Image.fromarray(res.reshape((height, width, 4)), 'RGBA')
#    img.show()
#
#
#if __name__ == "__main__":
#    exec()