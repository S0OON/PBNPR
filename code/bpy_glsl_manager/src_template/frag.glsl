// Blender 3.6 adds #version 330 automatically

layout (std140) uniform MyShaderParams {
    float u_intensity; // Bytes 0-3
    float u_R;         // Bytes 4-7
    float u_G;         // Bytes 8-11
    float u_B;         // Bytes 12-15
};
//Or uniform float u_intensity;
out vec4 fragCol;

void main() {
    vec3 col = vec3(u_R, u_G, u_B);
    fragCol = vec4(col * u_intensity, 1.0);
}