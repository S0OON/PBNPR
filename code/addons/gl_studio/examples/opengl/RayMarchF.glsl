#version 330

in vec3 position;

out vec4 fragColor;

uniform mat4 view_matrix;
uniform vec3 camera_pos;
uniform float time;

/*
// Mesh data (e.g., spheres/primitives) provided via buffer
// This allows you to update "mesh" positions every frame from the CPU
layout(set = 0, binding = 1) readonly buffer MeshData {
    vec4 primitives[]; // xyz = position, w = radius/scale
};]
*/

const int MAX_STEPS = 100;
const float MAX_DIST = 100.0;
const float SURF_DIST = 0.001;

// Signed Distance Function for a sphere
float sdSphere(vec3 p, vec3 center, float s) {
    return length(p - center) - s;
}

// Global Scene Distance function
float GetDist(vec3 p) {
    float d = p.y + 1.0; // Infinite floor plane

    // Loop through mesh data provided via uniforms/buffers
    for (int i = 0; i < primitives.length(); i++) {
        float primitiveDist = sdSphere(p, primitives[i].xyz, primitives[i].w);
        d = min(d, primitiveDist); // Union of all objects
    }

    return d;
}

// Primary Raymarching Loop
float RayMarch(vec3 ro, vec3 rd) {
    float dO = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * dO;
        float dS = GetDist(p);
        dO += dS;
        if (dO > MAX_DIST || abs(dS) < SURF_DIST) break;
    }
    return dO;
}

// Calculate Surface Normals via Gradient Estimation
vec3 GetNormal(vec3 p) {
    float d = GetDist(p);
    vec2 e = vec2(0.01, 0);
    vec3 n = d - vec3(
                GetDist(p - e.xyy),
                GetDist(p - e.yxy),
                GetDist(p - e.yyx)
            );
    return normalize(n);
}

void main() {
    // Screen coordinates (normalized -0.5 to 0.5)
    vec2 uv = (gl_FragCoord.xy - 0.5 * vec2(800, 600)) / 600.0;

    // Ray Origin and Direction
    vec3 ro = camPos;
    vec3 rd = normalize(vec3(uv.x, uv.y, 1.0));

    float d = RayMarch(ro, rd);

    if (d < MAX_DIST) {
        vec3 p = ro + rd * d;
        vec3 n = GetNormal(p);

        // Basic Diffuse Lighting
        float diff = dot(n, normalize(vec3(1, 2, 3))) * 0.5 + 0.5;
        fragColor = vec4(vec3(diff), 1.0);
    }
    else {
        // Background color
        fragColor = vec4(0.1, 0.1, 0.1, 1.0);
    }
}
