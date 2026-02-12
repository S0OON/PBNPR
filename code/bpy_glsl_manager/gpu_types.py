
# --- blender specific ---
bl_verts = 'verticies'
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
# --- Standard Output Names ---
ATTR_OUT_FRAG_COLOR = "fragColor" # Standard Fragment Output

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
