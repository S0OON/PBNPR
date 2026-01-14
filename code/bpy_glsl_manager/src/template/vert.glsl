in vec2 pos;
void main() {
    vec3 P = vec3(pos,1.0);
    gl_Position = vec4(P, 1.0);
}