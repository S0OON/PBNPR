import bpy,moderngl
from glsl_manager.gl.util import util_types as t 
from glsl_manager.gl.shader_pattren import ShaderBase, ui_base
import numpy as np
from typing import cast 
# this is a simple triangle implementation.

#======================================
class Shader(ShaderBase):
    NAME = "TriangleShader"
    VERT_SRC='''
#version 330
    in vec2 in_pos;
        void main() {
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
'''
    FRAG_SRC='''
#version 330
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
def execute_bake(self, context):
    try:
        self.bake_exec(context)
    except Exception as e:
        print(f"ERROR Failed to bake the shader [{__file__}], report: {e}")
        import traceback
        traceback.print_exc()

class bpy_ui(ui_base):
    # center
    shader_obj = Shader()
    Bake: bpy.props.BoolProperty(default=False,update=execute_bake) # pyright: ignore[reportInvalidTypeForm]
    baking_target_img: bpy.props.PointerProperty(type=bpy.types.Image) # pyright: ignore[reportInvalidTypeForm]
    show_settings: bpy.props.BoolProperty(default=False) # pyright: ignore[reportInvalidTypeForm]
    
    depth_test: bpy.props.EnumProperty(
        name="Depth Test", 
        description="How to handle depth buffer",
        items=[ (str(int(moderngl.DEPTH_TEST)), "Enabled", "Check depth, draw if closer"),
                ("0", "Disabled", "Ignore depth, draw on top"),],default=str(int(moderngl.DEPTH_TEST)) ) # pyright: ignore[reportInvalidTypeForm]
    
    blend_mode: bpy.props.EnumProperty(
        name="Blend Mode",
        description="How to blend colors",
        default="0",  # Opaque by default,
        items=[("0", "None", "Opaque, overwrite pixels"),
               (str(int(moderngl.BLEND)), "Alpha Blend", "Standard transparency"),]) # pyright: ignore[reportInvalidTypeForm]
    
    cull_face: bpy.props.EnumProperty(
        name="Cull Faces", 
        description="Which faces to skip drawing",
        default="0",
        items=[ ("0", "None", "Draw both front and back faces"),
                (str(int(moderngl.CULL_FACE)), "Back", "Don't draw back-facing faces"),]) # pyright: ignore[reportInvalidTypeForm]
    # peripheral
    color: bpy.props.FloatVectorProperty(
        name="Color",
        size=4,
        subtype="COLOR",
        default=(1.0, 1.0, 1.0, 1.0),
        min=(0.0),max=(1.0)
    ) # pyright: ignore[reportInvalidTypeForm]
    
    # ======================================
    def draw_self_to_panel_canvas(self, canvas: bpy.types.UILayout):
        # Main controls
        row = canvas.row(align=True)
        row.prop(self, 'Bake', text="", icon='RENDER_RESULT', icon_only=True)
        row.prop(self, 'baking_target_img', text="")
        # shader specific
        row = canvas.row(align=True)
        row.prop(self, 'color', text="")
        
        # Settings expander
        box = canvas.box()
        row = box.row()
        row.prop(self, 'show_settings', 
                icon='TRIA_DOWN' if self.show_settings else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Render Settings")
        
        if self.show_settings:
            col = box.column(align=True)
            col.prop(self, 'depth_test')
            col.prop(self, 'blend_mode')
            col.prop(self, 'cull_face') 
    
    def get_gl_flags(self):
        """Convert UI settings to ModernGL flags for ctx.enable()"""
        flags = 0
        
        if int(self.depth_test):
            flags |= moderngl.DEPTH_TEST
        if int(self.blend_mode):
            flags |= moderngl.BLEND
        if int(self.cull_face):
            flags |= moderngl.CULL_FACE 
            
        return flags if flags else None 
    
    def bake_exec(self, context):
        ui = self
        if not ui.Bake: return
            
        try:
            img = cast(bpy.types.Image, ui.baking_target_img)
            if not img: return
                
            shader = self.shader_obj
            if not shader:
                print(f"Shader object is None at {__file__}")
                return
            
            # Set uniforms
            shader._uniform(
                color=(ui.color[0], ui.color[1], ui.color[2], ui.color[3]),
            )
            
            # Upload geometry
            VAO = shader.ctx.buffer(coords.tobytes())
            shader.vao = shader.ctx.vertex_array(
                shader.prog,
                [(VAO, '2f', 'in_pos')]
            )

            # Execute render regarding flags
            gl_flags = self.get_gl_flags()
            p = shader._exec(
                img.size[0],img.size[1],
                gl_flags=gl_flags
            )
            
            # Assign to image
            img.pixels.foreach_set(p.astype(np.float32).reshape(-1) / 255.0)
            img.update()
        except Exception as e:
            print(f"Bake failed for {__file__}, REPORT: {e}")
            raise  # Re-raise to trigger outer exception handler
            
        finally:
            self.Bake = False


DESCRIPTION = t.SHADER_INTERP(
    UI=bpy_ui,
    SHADER=Shader
)