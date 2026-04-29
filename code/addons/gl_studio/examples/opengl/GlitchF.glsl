#version 330

in vec3 N;
in vec2 UVs;

out vec4 FragColor;

uniform vec2 resolution;

void main() {
    float d = dot(N,vec3(1.0,1.0,1.0));
    d = step(0.5,d);
    FragColor = vec4(vec3(d),1.0);
}
