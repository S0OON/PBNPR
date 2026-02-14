/*with:-
uColor
uPP
uOBJm
uCAMm
uPROJm
in vec3 V_N;
*/

void main() {
    vec3 worldNormal = normalize(mat3(uOBJm) * V_N);
    
    float Dot = dot(uPP,worldNormal);
    
    fragColor = uColor * vec4(vec3(Dot),1.0);
}