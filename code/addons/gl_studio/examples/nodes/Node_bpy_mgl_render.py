import dearpygui.dearpygui as dpg
import moderngl
import numpy as np
from PIL import Image
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
from gl_studio.util import util_types as t
def reset_gl_state(ctx: moderngl.Context):
    """
    Scrub the ModernGL state machine clean so it doesn't poison Blender's viewport.
    """
    if not ctx:
        return

    try:
        # 1. Unbind your custom Framebuffer. 
        # This points the GPU back to the default screen/window buffer.
        ctx.screen.use()

        # 2. Disable all intrusive flags
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        ctx.disable(moderngl.BLEND)
        ctx.disable(moderngl.PROGRAM_POINT_SIZE)

        # 3. Reset blending and depth equations to safe standard defaults
        ctx.blend_func = moderngl.DEFAULT_BLENDING
        ctx.blend_equation = moderngl.FUNC_ADD
        ctx.depth_func = '<'  # Standard Less-Than depth test
        ctx.cull_face = 'back'
        ctx.wireframe = False

        # 4. Clear any latent OpenGL errors in the buffer so Blender doesn't trip on them
        _ = ctx.error 

    except Exception as e:
        print(f"[GL Reset Error] Could not clean state: {e}")

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Isolated Triangle Test'

    def __init__(self, parent):
        super().__init__(parent)
        
        self.O_out = t.NodeSocket(dpg.generate_uuid(),t.NONE,'out->')
        # Zero sockets. Completely standalone.
        self._resgister_IO([], [self.O_out])

    def on_gui(self):
        super().on_gui()
        
        # The single button you asked for
        statics = self._create_static_attr()
        dpg.add_button(label="Draw & Show Triangle", callback=self.on_execute, parent=statics)

        out = self._create_output_attr(self.O_out)

    def on_execute(self):
        print(f"[{self.LABEL}] Initializing standalone render...")
        try:
            # 1. Create an isolated headless context and Framebuffer
            ctx = moderngl.create_context(standalone=True)
            fbo = ctx.simple_framebuffer((512, 512))
            fbo.use()

            # 2. Write a quick embedded shader (Position + Color)
            prog = ctx.program(
                vertex_shader='''
                    #version 330
                    in vec2 in_vert;
                    in vec3 in_color;
                    out vec3 v_color;
                    void main() {
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        v_color = in_color;
                    }
                ''',
                fragment_shader='''
                    #version 330
                    in vec3 v_color;
                    out vec4 f_color;
                    void main() {
                        f_color = vec4(v_color, 1.0);
                    }
                '''
            )

            # 3. Create Geometry Data: X, Y, R, G, B
            vertices = np.array([
                 0.0,  0.8,   1.0, 0.0, 0.0,  # Top vertex (Red)
                -0.8, -0.8,   0.0, 1.0, 0.0,  # Bottom-left (Green)
                 0.8, -0.8,   0.0, 0.0, 1.0,  # Bottom-right (Blue)
            ], dtype='f4')

            # 4. Upload to GPU
            vbo = ctx.buffer(vertices.tobytes())
            vao = ctx.vertex_array(prog, [(vbo, '2f 3f', 'in_vert', 'in_color')])

            # 5. Render
            ctx.clear(0.1, 0.1, 0.15, 1.0) # Dark gray-blue background
            vao.render(moderngl.TRIANGLES)

            # 6. Read back from GPU to CPU
            raw_pixels = fbo.read(components=4)
            image_array = np.frombuffer(raw_pixels, dtype=np.uint8).reshape((512, 512, 4))
            
            # OpenGL is upside down, flip it so PIL reads it right
            image_array = np.flipud(image_array)

            # 7. Show it!
            img = Image.fromarray(image_array, 'RGBA')
            img.show(title="Hello Triangle")
            print(f"[{self.LABEL}] Success!")

            # 8. Clean up VRAM
            vao.release()
            vbo.release()
            prog.release()
            fbo.release()
            ctx.release()

        except Exception as e:
            print(f"[{self.LABEL}] Render crashed: {e}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()