#version 330

in vec3 N;
in vec2 UVs;

out vec4 FragColor;

uniform vec2 resolution;

void main() {
    float edge = 1.0 - abs(dot(normalize(N), vec3(0, 0, 1)));
    edge = smoothstep(0.7, 1.0, edge);

    FragColor = vec4(vec3(edge), 1.0);
    FragColor = vec4(UVs, 0.0, 1.0);
}
