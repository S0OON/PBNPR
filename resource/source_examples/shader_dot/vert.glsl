layout (std140) uniform MyShaderParams {
    mat4 uOBJm;   // 0   - 63
    mat4 uCAMm;   // 64  - 127
    mat4 uPROJm;  // 128 - 191
    vec4 uCOL;    // 192 - 207
    vec4 uP;      // 208 - 222
}; // total = 224 bytes

in vec3 pos;
in vec3 normal;

out vec4 vColor;
out vec3 vNormal;
out vec3 point;
out float Depth;

void main() {
    vColor = uCOL;
    point = uP.xyz; 
    vec3 worldNormal = normalize(mat3(uOBJm) * normal);
    vNormal = normal;
    vec4 viewPos = uCAMm * uOBJm * vec4(pos, 1.0);
    Depth = -viewPos.z;
    
    gl_Position = uPROJm * viewPos;
}