import moderngl
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PIL import Image


class NODE_MGL_TRINGLE(BASE.NODE_INTERFACE):
    NODE_NAME = "mgl template"

    def __init__(self):
        super().__init__()
        self.add_output("Resaulted Tringle", type=t.RGBA)

    def on_stream(self):
        ctx = moderngl.create_context(standalone=True)

        # 2. Setup an Off-screen Framebuffer (FBO) to render into
        width, height = 512, 512
        fbo = ctx.simple_framebuffer(
            (width, height), components=3
        )  # 3 components = RGB
        fbo.use()

        # 3. Write the Shader Program
        prog = ctx.program(
            vertex_shader="""
                    #version 330
                    in vec2 in_position;
                    in vec3 in_color;
                    out vec3 v_color;

                    void main() {
                        gl_Position = vec4(in_position, 0.0, 1.0);
                        v_color = in_color;
                    }
                """,
            fragment_shader="""
                    #version 330
                    in vec3 v_color;
                    out vec3 f_color;

                    void main() {
                        f_color = v_color;
                    }
                """,
        )

        # 4. Define Triangle Data: (x, y) + (r, g, b)
        # Numpy 'f4' is required to match OpenGL 32-bit floats
        vertices = np.array(
            [
                # X,     Y,      R,   G,   B
                0.0,
                0.8,
                1.0,
                0.0,
                0.0,  # Top (Red)
                -0.8,
                -0.8,
                0.0,
                1.0,
                0.0,  # Bottom Left (Green)
                0.8,
                -0.8,
                0.0,
                0.0,
                1.0,  # Bottom Right (Blue)
            ],
            dtype="f4",
        )

        # 5. Create VBO and VAO
        vbo = ctx.buffer(vertices.tobytes())

        # The format '2f 3f' tells ModernGL:
        # "Read 2 floats for 'in_position', then 3 floats for 'in_color'"
        vao = ctx.vertex_array(prog, [(vbo, "2f 3f", "in_position", "in_color")])

        # 6. Render the frame
        ctx.clear(0.1, 0.1, 0.1)  # Dark gray background
        vao.render(moderngl.TRIANGLES)

        # 7. Extract raw pixels to PIL
        raw_bytes = fbo.read(components=3)
        image = Image.frombytes("RGB", (width, height), raw_bytes)

        # OpenGL renders bottom-up, so we must flip the image vertically
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # 8. Show the image and cleanup
        image.show()

        vao.release()
        vbo.release()
        prog.release()
