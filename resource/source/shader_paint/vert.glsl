layout (std140) uniform MyShaderParams {
    mat4 uOBJm;   // 0   - 63
    mat4 uCAMm;   // 64  - 127
    mat4 uPROJm;  // 128 - 191
    vec4 uCOL;    // 192 - 207
}; 

in vec3 pos;
out vec4 vColor;

void main() {
    vColor = uCOL;

    // Math Order: Projection * View * Model * Position
    vec4 world_pos = uOBJm * vec4(pos, 1.0);
    vec4 view_pos  = uCAMm * world_pos;
    gl_Position    = uPROJm * view_pos;
}