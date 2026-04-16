
#version 330
in vec2 in_vert;
in vec3 in_normal; // Normal vector of the surface
out vec3 v_normal;

void main() {
    v_normal = in_normal;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
