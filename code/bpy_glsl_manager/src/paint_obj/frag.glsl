in vec3 v_world_pos;

uniform vec4 uColor;
uniform float uLight;
uniform vec3 uLightPos;


void main() {
    float d = distance(v_world_pos, uLightPos);
    
    // Example: Make it darker as it gets further away
    float intensity = 1.0 / (d * d + 1.0); 
    gl_FragColor = uColor*intensity*uLight;
}