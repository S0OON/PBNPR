import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import sys

sys.path.append(r"D:\soon\projects\06_pythonShaders\code/src")
 
# -----------------------------------
def Init():
    if not hasattr(bpy, "_gpu_handlers"):
        bpy._gpu_handlers = {} 
    bpy.app.handlers.frame_change_pre.clear()
    bpy._gpu_handlers['res'] = [bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y]

def load_GLSL_pair(PATH_V: str, PATH_F: str):
    with open(PATH_V, 'r') as f: vert_code = f.read() 
    with open(PATH_F, 'r') as f: frag_code = f.read() 
    return vert_code, frag_code 

def clear_shader(NAME_SHADER: str = None):
    if not hasattr(bpy, "_gpu_handlers") or len(bpy._gpu_handlers) <= 0:
        return
        
    if NAME_SHADER:
        # Use .pop() to remove from the dict and get the data in one go 
        handle_data = bpy._gpu_handlers.pop(NAME_SHADER, None)
        if handle_data and len(handle_data) > 2:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handle_data[2], 'WINDOW') 
            except Exception as e:
                print(f"Failed to remove {NAME_SHADER}: {e}")
    else:
        # Nuclear option: Remove all visuals 
        for h in bpy._gpu_handlers.values():
            if len(h) > 2:
                try:
                    bpy.types.SpaceView3D.draw_handler_remove(h[2], 'WINDOW') 
                except:
                    pass
        # CRITICAL: Empty the registry so we start fresh 
        bpy._gpu_handlers.clear()
        
def remove_handler(NAME_:str):
    if not NAME_ or NAME_ not in bpy._gpu_handlers: 
        return
    bpy.types.SpaceView3D.draw_handler_remove(
        bpy._gpu_handlers[NAME_][2], 'WINDOW'
    )

def register_shader(
        SHADER_DESC:dict,
        USE_HANDLER = False,
        DRAW_SPACE: str = 'POST_VIEW',
        DRAW_REGION: str = 'WINDOW'
    ):
    if not SHADER_DESC: 
        print(f"Fainled registration due no desc dict")
        return 
    clear_shader(SHADER_DESC["NAME"]) 

    source = load_GLSL_pair(
        SHADER_DESC["PATH_VERT"],
        SHADER_DESC["PATH_FRAG"]
    ) 
    shader = gpu.types.GPUShader(source[0], source[1]) 
    
    #--------------------
    batch = SHADER_DESC["CALL_BATCH"](shader)
    handler = bpy.types.SpaceView3D.draw_handler_add (
        SHADER_DESC["CALL_BATCH_DRAW"], 
        (shader, batch), 
        DRAW_REGION, 
        DRAW_SPACE
    ) 
    bpy._gpu_handlers[SHADER_DESC["NAME"]] = [shader, batch, handler]
    if not USE_HANDLER:
        bpy.types.SpaceView3D.draw_handler_remove(handler,'WINDOW')

def bake_shader(
        SHADER_DESC:dict,
        NAME_TEX : str = '', 
        resX: int =0,
        resY: int =0,
        Save_to_Tex=False,
        follow_render_res=False
    ):
    if not SHADER_DESC:
        print("FAILED TO BAKE, no shader_desc dict present")
    NAME_SHADER = SHADER_DESC["NAME"]
    BATCH_DRAW_CALLBACK = SHADER_DESC["CALL_BATCH_DRAW"]

    if not NAME_TEX:
        NAME_TEX = NAME_SHADER
    if not resX or not resY or follow_render_res:
        resX, resY = bpy._gpu_handlers['res']

    img = bpy.data.images.get(NAME_TEX)
    if not img:
        img = bpy.data.images.new(NAME_TEX, resX, resY, alpha=True,float_buffer=True) 
    if follow_render_res:
        img.scale(bpy._gpu_handlers['res'][0],bpy._gpu_handlers['res'][1])
    W, H = img.size 

    if not Save_to_Tex:
        return img
    
    shader = bpy._gpu_handlers[NAME_SHADER][0]
    batch = bpy._gpu_handlers[NAME_SHADER][1]
    
    offscreen = gpu.types.GPUOffScreen(W, H) 
    with offscreen.bind():
        gpu.state.viewport_set(0, 0, W, H)
        BATCH_DRAW_CALLBACK(shader,batch)
        buffer = gpu.state.active_framebuffer_get().read_color(0, 0, W, H, 4, 0, 'FLOAT')
    
    buffer.dimensions = W * H * 4 
    img.pixels.foreach_set(buffer) 
    img.update() 
    
    offscreen.free() 
    return img

# ---------------

