in vec3 pos; 
uniform mat4 u_objM;
uniform mat4 u_camM;
uniform mat4 u_projM;

void main() {
    gl_Position =  u_projM * u_camM * u_objM * vec4(pos, 1.0);
}