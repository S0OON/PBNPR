uniform float u_f;
out vec4 fragCol;

void main() {
    vec3 F = vec3(u_f);
    fragCol = vec4(F, 1.0);
}