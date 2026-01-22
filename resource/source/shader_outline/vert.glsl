layout (std140) uniform MyShaderParams {
    mat4 uOBJm;   // 0   - 63
    mat4 uCAMm;   // 64  - 127
    mat4 uPROJm;  // 128 - 191
    vec4 uCOL;    // 192 - 207
    float uThic;     // 208 - 212 (full 223)
}; 

in vec3 pos;
in vec3 normal;

out vec4 vColor;

void main() {
    vColor = uCOL;

    vec3 worldNormal = normalize(mat3(uOBJm) * normal);

    vec3 expandedPos = pos + (normal * uThic);

    gl_Position = uPROJm * uCAMm * uOBJm * vec4(expandedPos, 1.0);
}