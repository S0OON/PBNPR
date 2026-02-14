/*with:-
uColor
uPP
uOBJm
uCAMm
uPROJm
V_N
in vec3 pos
in vec3 normal
*/

void main() {
    //OUT
    V_N = normal;
    //VIEW_marix
    vec4 viewPos = uCAMm * uOBJm * vec4(pos, 1.0);
    //Depth = -viewPos.z;
    
    //outptu
    gl_Position = uPROJm * viewPos;
}