import moderngl as g
import numpy as np
from gl_studio.util import util_types as t


class GL:
    def __init__(self, ctx: g.Context):
        self.ctx = ctx
        self.prog = None
        self.vao = None
        self.fbo = None

        # Keep track of generated objects so we can cleanly release them
        self._vbos = []
        self._textures = []
        self._outputs = {}

    def compile(
        self,
        V: str,
        F: str,
        dict_uni: dict,
        dict_res: dict,
        out_size=(t.RES_W, t.RES_H),
    ):
        # 1. Compile Shader
        self.prog = self.ctx.program(vertex_shader=V, fragment_shader=F)

        # 2. Handle Uniforms (Variables, Matrices, etc.)
        for name, val in dict_uni.items():
            if name in self.prog:
                # MGL handles most types dynamically, but arrays need .write()
                if isinstance(val, np.ndarray):
                    self.prog[name].write(val.tobytes())
                else:
                    self.prog[name].value = val

        # 3. Handle dict_res (Textures and Geometry/VBOs)
        vao_content = []
        tex_unit = 0

        for name, data in dict_res.items():
            if name not in self.prog:
                continue  # Skip data the shader doesn't care about!

            # TYPE A: It's an Image/Texture (Assuming a 3D numpy array: H, W, Channels)
            if isinstance(data, np.ndarray) and len(data.shape) == 3:
                h, w, c = data.shape
                tex = self.ctx.texture((w, h), c, data.tobytes())  # 1. Upload to GPU
                tex.use(location=tex_unit)  # 2. Put in a "Slot"
                self.prog[name].value = tex_unit  # 3. Tell the shader which slot!
                self._textures.append(tex)
                tex_unit += 1

            # TYPE B: It's Vertex Data / UVs (Assuming a 2D numpy array: Vertices, Components)
            elif isinstance(data, np.ndarray) and len(data.shape) == 2:
                components = data.shape[1]  # e.g., 3 for vec3 position, 2 for vec2 UV
                vbo = self.ctx.buffer(data.astype("f4").tobytes())

                # Format string for MGL (e.g., '3f', '2f')
                mgl_format = f"{components}f"

                # Append to our dynamic VAO list: (buffer, format, attribute_name)
                vao_content.append((vbo, mgl_format, name))
                self._vbos.append(vbo)

        # 4. Build Dynamic VAO
        # If no geometry was provided, we can't really draw, but we handle it safely
        if vao_content:
            self.vao = self.ctx.vertex_array(self.prog, vao_content)
        else:
            print("Warning: No vertex data provided for VAO!")

        # 5. Handle Outputs (FBO)
        # We create a dictionary of output textures. You can expand this to check for depth.
        out_tex = self.ctx.texture(out_size, 4)  # RGBA combined output
        self.fbo = self.ctx.framebuffer(color_attachments=[out_tex])
        self._outputs["Combined"] = out_tex

    def execute(self) -> dict:
        if not self.vao or not self.fbo:
            return {}

        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.vao.render(g.TRIANGLES)

        # Extract data from GPU back to CPU/Numpy for your node outputs
        result_dict = {}
        for name, tex in self._outputs.items():
            raw = tex.read()
            # Convert back to numpy array (H, W, 4)
            arr = np.frombuffer(raw, dtype=np.uint8).reshape(
                tex.height, tex.width, tex.components
            )
            result_dict[name] = arr

        return result_dict

    def release(self):
        # END: ALWAYS CLEAR dynamically generated resources
        if self.vao:
            self.vao.release()
        if self.fbo:
            self.fbo.release()
        if self.prog:
            self.prog.release()
        for vbo in self._vbos:
            vbo.release()
        for tex in self._textures:
            tex.release()
        for out in self._outputs.values():
            out.release()
