import moderngl as gl
import numpy as np
from gl_studio.util import util_types as t

class MGL:

    def __init__(self, ctx:gl.Context):
        # Allow passing an existing context, otherwise create a standalone one
        self.ctx = ctx

        # Resource caches
        self.prog = None
        self.fbo = None
        self.col = None
        self.depth = None
        self.vbos = {}   # Map: name -> (vbo_object, format, shape)

        self.vao = None
        self.texs = {}   # Map: name -> texture_object

        self.w = int(t.RES_W)
        self.h = int(t.RES_H)
        self.src_v = t.SRC_SCREEN_VERT
        self.src_f = t.SRC_SCREEN_FRAG
        self.def_screen_pos = t.SCREEN_VERTS
        self.def_screen_uv = t.SCREEN_UV

        # Trackers to know when we *actually* need to rebuild
        self._cached_v = ""
        self._cached_f = ""
        self._cached_res = (0, 0)

    def compile(self):
        needs_rebuild = False

        # 1. Smart Shader Compilation
        if self.src_v != self._cached_v or self.src_f != self._cached_f:
            if self.prog:
                self.prog.release()
            self.prog = self.ctx.program(
                vertex_shader=self.src_v,
                fragment_shader=self.src_f,
            )
            self._cached_v = self.src_v
            self._cached_f = self.src_f
            needs_rebuild = True # VAO needs rebuilding if shader changes

        # 2. Smart FBO Allocation
        if (self.w, self.h) != self._cached_res:
            if self.fbo:
                self.fbo.release()
                self.col.release()
                self.depth.release()

            self.col = self.ctx.renderbuffer((self.w, self.h), dtype='f4')
            self.depth = self.ctx.depth_renderbuffer((self.w, self.h))
            self.fbo = self.ctx.framebuffer(color_attachments=[self.col], depth_attachment=self.depth)
            self._cached_res = (self.w, self.h)

        return needs_rebuild

    def uniforms(self, uniforms_dict):
        if not self.prog:
            return

        uniforms = uniforms_dict if isinstance(uniforms_dict, dict) else {}

        if t.RES not in uniforms.keys():
            uniforms[t.RES] = (self.w, self.h)

        for name, data in uniforms.items():
            if name in self.prog:
                if isinstance(data, (list, tuple, np.ndarray)) and len(data) == 16:
                    self.prog[name].write(np.array(data, dtype="f4").tobytes())
                else:
                    self.prog[name].value = data

    def uniforms_textures(self, textures_dict):
        if not self.prog:
            return

        textures = textures_dict if isinstance(textures_dict, dict) else {}
        texture_location = 0

        for name, tex_obj in textures.items():
            if name in self.prog:
                if isinstance(tex_obj, np.ndarray):
                    # Robust unpacking: (Height, Width, [Channels])
                    if tex_obj.ndim == 3:
                        h, w, c = tex_obj.shape
                    elif tex_obj.ndim == 2:
                        h, w = tex_obj.shape
                        c = 1
                    else:
                        print(f"[MGL CLASS] texture {name} has invalid dimensions: {tex_obj.shape}")
                        continue

                    pixels = tex_obj.tobytes()
                    dtype = 'f4'

                    # UPDATE existing texture if shape matches, otherwise RE-CREATE
                    # ModernGL texture.size is (Width, Height)
                    if name in self.texs and self.texs[name].size == (w, h):
                        self.texs[name].write(pixels)
                    else:
                        if name in self.texs:
                            self.texs[name].release()

                        tex = self.ctx.texture((w, h), c, data=pixels, dtype=dtype)
                        tex.filter = (gl.NEAREST, gl.NEAREST)
                        self.texs[name] = tex

                    self.texs[name].use(location=texture_location)
                    self.prog[name].value = texture_location
                    texture_location += 1
                else:
                    print("[MGL CLASS] texture ", name, " NON np.array!")

    def vertex_attributes(self, attributes_dict, force_rebuild=False):
        """Updates existing VBOs with new data. Only rebuilds VAO if topologies change."""
        if not self.prog:
            return

        attrs = attributes_dict if isinstance(attributes_dict, dict) else {}
        if t.POS not in attrs:
            attrs[t.POS] = self.def_screen_pos
        if t.UV not in attrs:
            attrs[t.UV] = self.def_screen_uv

        vao_blueprint = []
        rebuild_vao = force_rebuild or (self.vao is None)

        for name, obj in attrs.items():
            if name in self.prog and isinstance(obj, np.ndarray):
                fmt = t.get_mgl_format(obj)
                obj_bytes = obj.tobytes()

                # Check if we can just update the existing VBO
                if name in self.vbos and self.vbos[name][1] == fmt and self.vbos[name][2] == obj.shape:
                    vbo = self.vbos[name][0]
                    vbo.write(obj_bytes) # FAST path: Update existing buffer
                else:
                    # SLOW path: Allocate new buffer
                    if name in self.vbos:
                        self.vbos[name][0].release()

                    vbo = self.ctx.buffer(obj_bytes)
                    self.vbos[name] = (vbo, fmt, obj.shape)
                    rebuild_vao = True

                vao_blueprint.append((vbo, fmt, name))

        if rebuild_vao and vao_blueprint:
            if self.vao:
                self.vao.release()
            self.vao = self.ctx.vertex_array(self.prog, vao_blueprint)

    def render(self, render_flag):
        if not self.vao or not self.fbo:
            return None, None

        self.fbo.use()
        self.ctx.clear()
        self.vao.render(render_flag)

        raw = self.fbo.read(components=4, dtype='f4')
        rawD = self.fbo.read(attachment=-1, components=1, dtype='f4')

        return raw, rawD

    def clear(self):
        """Safely destroys all GPU objects. Call ONLY when deleting the node."""
        for tex_name, tex in self.texs.items():
            tex.release()
        self.texs.clear()

        if self.vao:
            self.vao.release()
            self.vao = None

        for vbo_name, (vbo, fmt, shape) in self.vbos.items():
            vbo.release()
        self.vbos.clear()

        if self.prog:
            self.prog.release()
            self.prog = None

        if self.fbo:
            self.fbo.release()
            self.col.release()
            self.depth.release()
            self.fbo = None

        self.ctx.gc()
