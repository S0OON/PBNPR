#version 330

in vec3 positions;
in vec3 normals;
in vec2 UVMap;

out vec3 W_POS;
out vec3 L_POS;

uniform mat4 world_matrix;
uniform mat4 view_matrix;
uniform mat4 proj_matrix;

void main() {
    L_POS = positions;

    vec4 wp = world_matrix * vec4(positions, 1.0);
    W_POS = wp.xyz;

    gl_Position = proj_matrix * view_matrix * wp;
}
