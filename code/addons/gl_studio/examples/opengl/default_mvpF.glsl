#version 330

in vec2 UVS;

out vec4 FragColor;

uniform sampler2D A;

void main() {
    FragColor = texture(A, UVS);
}
