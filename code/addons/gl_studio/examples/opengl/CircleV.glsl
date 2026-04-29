#version 330

in vec2 positions;
in vec2 UVMap;

out vec2 UV;

void main() {
    UV = UVMap;
    gl_Position = vec4(positions,0.0, 1.0);
}
