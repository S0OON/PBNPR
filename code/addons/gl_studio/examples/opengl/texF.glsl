#version 330

in vec2 UVs;
out vec4 FragColor;

uniform sampler2D CH_0_Steve;

void main() {
    FragColor = texture(CH_0_Steve, UVs);
}
