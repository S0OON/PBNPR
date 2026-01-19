
out vec4 fragColor;

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(uCamPos - v_world_pos);

    float rim = 1.0 - max(dot(N, V), 0.0);

    // Shape the rim
    rim = smoothstep(0.4, 1.0, rim);

    vec3 baseColor = vec3(0.6);
    vec3 rimColor  = vec3(1.0);

    fragColor = vec4(baseColor + rim * rimColor, 1.0);
}
