in vec3 pos;
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;

out vec3 v_world_pos; // Send this to fragment shader

void main() {
    vec4 world_pos = uModel * vec4(pos, 1.0);
    v_world_pos = world_pos.xyz;
    
    gl_Position = uProj * uView * world_pos;
}