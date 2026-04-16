#version 330
in vec3 v_normal;
out vec4 f_color;

uniform vec3 light_dir; // The direction of our light source

void main() {
    // DOT PRODUCT EXAMPLE:
    // dot(a, b) returns 1.0 if vectors face the same way, 0 if perpendicular.
    // We use 'max' to ensure we don't get negative light.
    float brightness = max(dot(normalize(v_normal), normalize(light_dir)), 0.0);

    vec3 base_color = vec3(0.2, 0.6, 1.0); // Blueish surface
    f_color = vec4(base_color * brightness, 1.0);
}
