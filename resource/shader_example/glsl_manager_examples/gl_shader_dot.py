import bpy,moderngl
from glsl_manager.gl.util import util_types as t
from glsl_manager.gl.shader_pattren import ShaderBase, ui_base
import numpy as np
from typing import cast 
# this is a simple dot product implementation.

mOBJ = 'mOBJ'
mCAM = 'mCAM'
mPROJ = 'mPROJ'
COLOR = 'color'
#======================================
class Shader(ShaderBase):
    NAME = "TriangleShader"
    VERT_SRC= (
'#version 330\n'
    f'uniform mat4 {mOBJ };'
    f'uniform mat4 {mCAM };'
    f'uniform mat4 {mPROJ};'

    f'in vec3 {t.ATTR_POS};'
    f'in vec3 {t.ATTR_NORMAL};'
    f'out vec3 N;'
        'void main() {'
            f'N={t.ATTR_NORMAL};'
            f'gl_Position = {mPROJ}* {mCAM}*{mOBJ}*vec4({t.ATTR_POS}, 1.0);'
        '}'
)
    FRAG_SRC=( 
'#version 330\n'
    f'uniform vec4 {COLOR};'
    f'uniform vec3 {t.ATTR_POINT};'

    f'in vec3 N;'
    f'out vec4 {t.ATTR_OUT_FRAG_COLOR};'
        'void main() {'
            'vec3 A = normalize(point);'
            'vec3 B = normalize(N);'
            f'float Dota = dot(A,B);'
            f'{t.ATTR_OUT_FRAG_COLOR} = vec4( Dota * {COLOR}.rgb, {COLOR}.a);'
        '}'
)
    def __init__(self):
        super().__init__()

#======================================
coords = np.array([(-0.5, -0.5,0.0), (0.5, -0.5,0.0), (0.0, 0.5,0.0)], dtype=np.float32) # cool tringle coordinates

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
        default="LESS_EQUAL", # Changed from no default to valid dict key
        items=[(i,i,'') for i in t.DEPTH_FUNCS.keys()] ) # pyright: ignore[reportInvalidTypeForm]
    
    blend_mode: bpy.props.EnumProperty(
        name="Blend Mode",
        description="How to blend colors",
        default="NONE",  # Changed from "0" to valid dict key
        items=[(i,i,'') for i in t.BLEND_PRESETS.keys()]) # pyright: ignore[reportInvalidTypeForm]
    
    cull_face: bpy.props.EnumProperty(
        name="Cull Faces", 
        description="Which faces to skip drawing",
        default="BACK",  # Changed from "0" to valid dict key
        items=[(i,i,'') for i in t.CULL_MODES.keys()] ) # pyright: ignore[reportInvalidTypeForm]
    # peripheral
    clear : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    color: bpy.props.FloatVectorProperty(
        name="Color",
        size=4,
        subtype="COLOR",
        default=(1.0, 1.0, 1.0, 1.0),
        min=(0.0),max=(1.0)
    ) # pyright: ignore[reportInvalidTypeForm]
    Object : bpy.props.PointerProperty(type=bpy.types.Object) # pyright: ignore[reportInvalidTypeForm]
    vector : bpy.props.FloatVectorProperty(subtype='XYZ') # pyright: ignore[reportInvalidTypeForm]
    # ======================================
    def draw_self_to_panel_canvas(self, canvas: bpy.types.UILayout):
        # Main controls
        row = canvas.row(align=True)
        row.prop(self, 'Bake', text="", icon='RENDER_RESULT', icon_only=True)
        row.prop(self, 'baking_target_img', text="")
        row.prop(self, 'clear',emboss=True)
        # shader specific
        row = canvas.row(align=True)
        row.prop(self, 'color', text="")
        row = canvas.row(align=True)
        row.prop(self, 'Object')
        row = canvas.row()
        row.prop(self, 'vector')
        
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
    
    def _get_gl_flags(self): # Note the underscore prefix, this is an internal helper method not meant to be called from outside.
        """Convert UI settings to ModernGL flags for ctx.enable()"""
        flags = 0
        
        if self.depth_test != 'NONE':
            flags |= moderngl.DEPTH_TEST
        if self.blend_mode != 'NONE':
            flags |= moderngl.BLEND
        if self.cull_face != 'NONE':
            flags |= moderngl.CULL_FACE 
            
        return flags if flags else None
    
    def _get_mesh_data_for_gpu(self,obj:bpy.types.Object):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj  = obj.evaluated_get(depsgraph)
        mesh      = eval_obj.to_mesh()
        mesh.calc_loop_triangles()
        
        tris_count = len(mesh.loop_triangles)
        
        # 1. Get the Loop Indices (The specific corners of every triangle)
        loops_indices = np.empty((tris_count * 3), dtype=np.int32)
        mesh.loop_triangles.foreach_get("loops", loops_indices)

        # 2. Get Vertex Indices (Which vertex does each corner point to?)
        vertex_indices = np.empty((tris_count * 3), dtype=np.int32)
        mesh.loop_triangles.foreach_get(t.bl_verts, vertex_indices)

        # --- A. Collect Positions ---
        # Get all unique positions, then map them to our triangle corners
        all_pos = np.empty((len(mesh.vertices), 3), dtype=np.float32)
        mesh.vertices.foreach_get(t.bl_Co, all_pos.reshape(-1))
        
        # Create the final flat array of positions (3 for every triangle)
        final_pos = all_pos[vertex_indices]

        # --- B. Collect Normals ---
        # Get normals from LOOPS (This preserves Sharp Edges and Custom Split Normals, like bleeding)
        all_normals = np.empty((len(mesh.loops), 3), dtype=np.float32)
        mesh.loops.foreach_get(t.bl_normal, all_normals.reshape(-1))
        
        # final flat array of normals
        final_normals = all_normals[loops_indices]

        eval_obj.to_mesh_clear() # Clean up (safe in 4.0/5.0 context depending on usage)
        
        return loops_indices ,final_pos, final_normals

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
            
            obj = cast(bpy.types.Object,ui.Object)
            if not obj: return

            point = ui.vector
            if point is None: return

            deps = bpy.context.evaluated_depsgraph_get()
            w,h     = img.size[0],img.size[1]
            cam     = cast(bpy.types.Camera,bpy.context.scene.camera)
            m_world = np.array(obj.matrix_world.transposed(),                     dtype=np.float32).flatten()
            m_view  = np.array(cam.matrix_world.inverted().transposed(),          dtype=np.float32).flatten()
            m_proj  = np.array(cam.calc_matrix_camera(deps,x=w,y=h).transposed(), dtype=np.float32).flatten()

            shader._uniform(
                color=(ui.color[0], ui.color[1], ui.color[2], ui.color[3]),
                mOBJ = m_world,
                mCAM = m_view,
                mPROJ = m_proj,
                point = (point[0],point[1],point[2])
            )
            
            # Upload geometry
            i,p,n = cast(np.array,self._get_mesh_data_for_gpu(obj))

            VAO_p = shader.ctx.buffer(p)
            VAO_n = shader.ctx.buffer(n)
            shader.vao = shader.ctx.vertex_array(shader.prog,[
                    (VAO_p, '3f', t.ATTR_POS),
                    (VAO_n, '3f', t.ATTR_NORMAL)
                 ])
            
            f = ui._get_gl_flags()
            if f: 
                shader.ctx.enable(f)
            if ui.depth_test != 'NONE':
                shader.ctx.depth_func = t.DEPTH_FUNCS[ui.depth_test] 

            if ui.blend_mode != 'NONE':
                shader.ctx.blend_func = t.BLEND_PRESETS[ui.blend_mode] 

            if ui.cull_face != 'NONE':
                shader.ctx.cull_face = t.CULL_MODES[ui.cull_face]
                
            p = shader._exec(w,h,clear=ui.clear)
            
            # Assign to image
            img.pixels.foreach_set(p.astype(np.float32).reshape(-1) / 255.0)
            img.update()
        except Exception as e:
            print(f"Bake failed for {__file__}, REPORT: {e}")
            raise  # Re-raise to trigger outer exception handler
            
        finally:
            self.Bake = False
    
    def unregister(self):
        self.shader_obj._release()

DESCRIPTION = t.SHADER_INTERP(
    UI=bpy_ui,
    SHADER=Shader
)