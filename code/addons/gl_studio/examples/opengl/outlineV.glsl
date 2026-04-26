#version 330

in vec3 positions;
in vec3 normals;
in vec2 UVMap;

out vec2 UVs;
out vec3 N;

uniform mat4 world_matrix;
uniform mat4 view_matrix;
uniform mat4 proj_matrix;

void main() {
    UVs = UVMap;
    N = normals;

    gl_Position = proj_matrix * view_matrix * world_matrix * vec4(positions, 1.0);
}
