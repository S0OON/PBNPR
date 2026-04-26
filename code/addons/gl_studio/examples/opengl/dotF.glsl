#version 330

in vec3 N;

out vec4 f_color;

void main() {
    float F = dot(N, vec3(1.0, 1.0, 1.0));

    f_color = vec4(vec3(F), 1.0);
}
