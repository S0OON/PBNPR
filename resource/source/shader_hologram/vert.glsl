layout (std140) uniform MyShaderParams {
    mat4 uOBJm;   // 0   - 63
    mat4 uCAMm;   // 64  - 127
    mat4 uPROJm;  // 128 - 191
    vec4 uCOL;    // 192 - 207
    float ut;     // 208 - 212 (full 223)
}; 

in vec3 pos;

out vec4 vColor;
out float u_time;

void main() {
    vColor = uCOL;
    u_time = ut;

    float wave = sin(pos.y * 10.0 + u_time * 5.0) * 0.2;
    vec3 newPos = pos + vec4(wave, 0.0, 0.0, 0.0).xyz;

    gl_Position = uPROJm * uCAMm * uOBJm * vec4(newPos, 1.0);
}