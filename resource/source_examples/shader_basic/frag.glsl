
in vec4 vColor;
in vec3 vNormal;
in vec3 point;
in float Depth;

out vec4 fragCol;

void main() {
    float Dot = dot(point,vNormal);
    
    fragCol = vColor * vec4(vec3(Dot),1.0);
}