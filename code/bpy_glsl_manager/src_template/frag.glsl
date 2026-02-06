// This file belongs to S00N's PBNPR Blender Add-on
// all rights reserved (C) 2024 S00N
void main() {
    // Access members via the instance name 'u_params' defined in CreateInfo
    vec3 col = vec3(
        u_params.u_R, 
        u_params.u_G, 
        u_params.u_B
        );
    fragCol = vec4(col * u_params.u_intensity, 1.0);
}