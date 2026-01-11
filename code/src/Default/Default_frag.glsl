uniform float u_f; 
out vec4 fragCol;


void main() {
    fragCol = vec4(vec3(u_f),1.0);
}