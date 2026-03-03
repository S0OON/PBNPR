from dataclasses import dataclass
from typing import Callable, Type
import moderngl

@dataclass
class SHADER_INTERP:
    """
    This is for the addon's internals to understand the current python file.
    
    data = UI(bpy.type.propertyGroup),SHADER(a provided default pattern provided in glsl_manager.gl.shader_pattren)
    """
    UI     : Type
    SHADER : Type

import moderngl
# --- 1. CONTEXT FLAGS (For ctx.enable / ctx.disable) ---
# Combine these using bitwise OR (|) when building flags for ctx.enable()
GL_FLAGS = {
    'DEPTH_TEST'        : moderngl.DEPTH_TEST,
    'CULL_FACE'         : moderngl.CULL_FACE,
    'BLEND'             : moderngl.BLEND,
    'PROGRAM_POINT_SIZE': moderngl.PROGRAM_POINT_SIZE,
    'RASTERIZER_DISCARD': moderngl.RASTERIZER_DISCARD,
    'NONE': 0  # Safe fallback if UI is set to None/Off
}

# --- 2. DEPTH FUNCTIONS (For ctx.depth_func) ---
# ModernGL relies on simple math strings instead of confusing C++ integer constants.
DEPTH_FUNCS = {
    'LESS'      : '<',      # Standard: Draw if closer to camera
    'LESS_EQUAL': '<=',     # Draw if closer or equal (ModernGL Default)
    'EQUAL'     : '==',     # Draw only if exactly equal
    'NOT_EQUAL' : '!=',     # Draw if different
    'ALWAYS'    : '1',      # Always draw, ignoring depth
    'NEVER'     : '0'       # Never draw
}

# --- 3. CULL FACE MODES (For ctx.cull_face) ---
# ModernGL uses simple strings.
CULL_MODES = {
    'BACK'          : 'back',            # Standard optimization: Don't draw inside faces
    'FRONT'         : 'front',           # Inside-out view: Don't draw outside faces
    'FRONT_AND_BACK': 'front_and_back'   # Draw nothing, idk wtf this
}

# --- 4. BLEND PRESETS (For ctx.blend_func) ---
# Format is a tuple: (Source, Destination)
BLEND_PRESETS = {
    'ALPHA'        : (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA), # Standard transparency
    'ADDITIVE'     : (moderngl.ONE,       moderngl.ONE),                 # Glows, fire, lasers
    'MULTIPLY'     : (moderngl.DST_COLOR, moderngl.ZERO),                # Darkening, shadows
    'PREMULTIPLIED': (moderngl.ONE,       moderngl.ONE_MINUS_SRC_ALPHA), # Premultiplied alpha
    'NONE': None                                                         # Disable blending entirely
}

# --- 5. DATA TYPES (For buffer attributes) ---
# ModernGL uses struct format strings (data type + bytes per component).
# e.g., 'f4' = Float 4-byte (32-bit float). 'i1' = Integer 1-byte(idk i think its either an boolean).
GL_TYPES = {
    'FLOAT' : 'f4',      # 32-bit float (Standard for vertices/normals)
    'DOUBLE': 'f8',      # 64-bit float
    'INT'   : 'i4',      # 32-bit signed integer
    'UINT'  : 'u4',      # 32-bit unsigned integer
    'SHORT' : 'i2',      # 16-bit signed integer
    'BYTE'  : 'i1',      # 8-bit signed integer
    'UBYTE' : 'f1'       # 8-bit unsigned int (Standard for 0-255 color data)
}

# --- 6. PRIMITIVE TYPES (For vao.render(mode=...)) ---
# These are the standard geometric drawing modes.
PRIMITIVES = {
    'POINTS'        : moderngl.POINTS,
    'LINES'         : moderngl.LINES,
    'LINE_STRIP'    : moderngl.LINE_STRIP,
    'LINE_LOOP'     : moderngl.LINE_LOOP,
    'TRIANGLES'     : moderngl.TRIANGLES,       # Standard 3D 
    'TRIANGLE_STRIP': moderngl.TRIANGLE_STRIP,
    'TRIANGLE_FAN'  : moderngl.TRIANGLE_FAN
}

# --- blender specific ---
bl_verts = 'vertices'
bl_Co = 'co'
bl_normal = 'normal'
bl_loop_triangles = 'loop_triangles'

# --- Data Types (for CreateInfo) ---
FLOAT    = 'FLOAT'
INT      = 'INT'
UINT     = 'UINT'
VEC2     = 'VEC2'
VEC3     = 'VEC3'
VEC4     = 'VEC4'
MAT3     = 'MAT3'
MAT4     = 'MAT4'
IVEC2    = 'IVEC2'
IVEC3    = 'IVEC3'
IVEC4    = 'IVEC4'
UVEC2    = 'UVEC2'
UVEC3    = 'UVEC3'
UVEC4    = 'UVEC4'
# --- Texture Sampler Types ---
SAMPLER_1D           = 'FLOAT_1D'
SAMPLER_2D           = 'FLOAT_2D'
SAMPLER_3D           = 'FLOAT_3D'
SAMPLER_CUBE         = 'FLOAT_CUBE'
SAMPLER_BUFFER       = 'FLOAT_BUFFER'
SAMPLER_1D_ARRAY     = 'FLOAT_1D_ARRAY'
SAMPLER_2D_ARRAY     = 'FLOAT_2D_ARRAY'
SAMPLER_CUBE_ARRAY   = 'FLOAT_CUBE_ARRAY'
SAMPLER_2D_SHADOW    = 'FLOAT_2D_SHADOW'  # For depth maps

# --- Standard Attribute Names (Blender Conventions) ---
ATTR_POS      = "pos"      # Standard position (vec3)
ATTR_NORMAL   = "normal"   # Standard normal (vec3)
ATTR_UV       = "uv"       # Standard UV map (vec2)
ATTR_COLOR    = "color"    # Vertex color (vec4)
ATTR_TANGENT  = "tangent"  # Tangent (vec4)
ATTR_POINT    = "point"    # Point (vec3)
ATTR_VIEW_MAT = "viewMat"  # View Matrix (mat4)
# --- Standard Output Names ---
ATTR_OUT_FRAG_COLOR = "fragColor" # Standard Fragment Output
ATTR_OUT_V          = "gl_Position"

# --- GPU State Constants ---
DEPTH_NONE    = 'NONE'       # Disable depth testing
DEPTH_ALWAYS  = 'ALWAYS'     # Always draw, regardless of depth
DEPTH_LESS    = 'LESS'       # Standard: Draw if closer
DEPTH_LEQUAL  = 'LESS_EQUAL' # Draw if closer or equal (Default)
DEPTH_GREATER = 'GREATER'    # Draw if further away
DEPTH_GEQUAL  = 'GREATER_EQUAL'

BLEND_NONE    = 'NONE'
BLEND_ALPHA   = 'ALPHA'              # Standard transparency
BLEND_ADD     = 'ADDITIVE'           # Light accumulation (fire, lasers)
BLEND_ADD_ALPHA = 'ADDITIVE_ALPHA'   # Additive but respects alpha
BLEND_MULTIPLY = 'MULTIPLY'          # Darkening (shadows)

CULL_NONE     = 'NONE'     # Draw both sides of faces
CULL_BACK     = 'BACK'     # Don't draw back-faces (Standard optimization)
CULL_FRONT    = 'FRONT'    # Don't draw front-faces (Inside-out view)

# --- Primitive Types (for batch_for_shader) ---
PRIM_POINTS     = 'POINTS'
PRIM_LINES      = 'LINES'
PRIM_TRIS       = 'TRIS'
PRIM_LINE_STRIP = 'LINE_STRIP'
PRIM_TRI_STRIP  = 'TRI_STRIP'

#--- utlis ---
SHADER_V = 'vert.glsl'
SHADER_F = 'frag.glsl'
SHADER_DRAW_REGION_WINDOW  = 'WINDOW'
SHADER_DRAW_TYPE_POST_PIXEL= 'POST_PIXEL'# Usually  for 2D drawing and 
SHADER_DRAW_TYPE_POST_VIEW = 'POST_VIEW'  # for 3D drawing. 
SHADER_DRAW_TYPE_PRE_VIEW  = 'PRE_VIEW'   # for 3D drawing before the main scene is drawn. Useful for backgrounds or effects that should appear behind everything else.
