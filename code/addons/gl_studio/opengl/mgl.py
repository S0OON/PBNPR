import moderngl as gl
import numpy as np


class SHADER:
    def __init__(self) -> None:
        self.ctx = gl.create_context(standalone=True)

        # State trackers for safe cleanup
        self.prog = None
        self.fbo = None
        self.vao = None
        self.vbos = []  # Keep track of dynamic buffers!

        # Default shaders
        self.src_v = """
            #version 330
            in vec3 in_position;
            void main() {
                gl_Position = vec4(in_position, 1.0);
            }
        """
        self.src_f = """
            #version 330

            out vec4 f_color;
            void main() {
                f_color = vec4(1.0);
            }
        """

    def compile(self, w, h):
        """Compiles the shader program and sets up the render target."""
        # 1. Clear old data if re-compiling to prevent VRAM leaks
        if self.prog:
            self.prog.release()
        if self.fbo:
            self.fbo.release()

        # 2. Compile Shader
        self.prog = self.ctx.program(
            vertex_shader=self.src_v,
            fragment_shader=self.src_f,
        )

        # 3. Setup Off-screen Framebuffer
        width, height = int(w), int(h)
        self.fbo = self.ctx.simple_framebuffer((width, height), components=3)

    def uniforms(self, uniforms_dict):
        """Pushes global variables to the shader."""
        if not self.prog or not uniforms_dict:
            return

        # Must use .items() to get both key and value!
        for name, data in uniforms_dict.items():
            if name in self.prog:
                # Handle flattened matrices (16 floats) using raw bytes
                if isinstance(data, (list, tuple)) and len(data) == 16:
                    self.prog[name].write(np.array(data, dtype="f4").tobytes())
                # Handle normal values (floats, vectors)
                else:
                    self.prog[name].value = data

    def vertex_attributes(self, attributes_dict):
        """Generates VBOs and creates the VAO layout."""
        if not self.prog or not attributes_dict:
            return

        vao_blueprint = []
        self.vbos = []  # Reset VBO tracker

        for attr_name, attr_obj in attributes_dict.items():
            if attr_name in self.prog:
                # Create buffer and track it
                vbo = self.ctx.buffer(attr_obj.data)
                self.vbos.append(vbo)

                # Add to blueprint
                vao_blueprint.append((vbo, attr_obj.fmt, attr_name))

        if not vao_blueprint:
            return

        # Build and store the VAO
        self.vao = self.ctx.vertex_array(self.prog, vao_blueprint)

    def render(self):
        """Executes the draw call and returns RGB bytes."""
        if not self.vao or not self.fbo:
            return None

        # Lock onto the FBO right before rendering
        self.fbo.use()
        self.ctx.clear(0.1, 0.1, 0.1)

        self.ctx.enable(gl.DEPTH_TEST)
        self.vao.render(gl.TRIANGLES)
        self.ctx.disable(gl.DEPTH_TEST)

        return self.fbo.read(components=3)

    def clear(self):
        """Safely destroys all GPU objects to free VRAM."""
        if self.vao:
            self.vao.release()
            self.vao = None

        for vbo in self.vbos:
            vbo.release()
        self.vbos.clear()

        if self.prog:
            self.prog.release()
            self.prog = None

        if self.fbo:
            self.fbo.release()
            self.fbo = None
