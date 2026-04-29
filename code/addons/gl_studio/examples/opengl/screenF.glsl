#version 330

in vec2 UV;

out vec4 fragCol;

uniform vec2 resolution;

void main() {
    fragCol = vec4(UV, 0.0, 1.0);
}
