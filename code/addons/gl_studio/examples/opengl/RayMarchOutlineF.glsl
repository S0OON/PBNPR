#version 330

/*
    Direct Raymarching with Uniform Data
    ------------------------------------
    This version uses a direct Uniform Array instead of a texture.
    It's easier to understand and works directly with "RGBA" (vec4)
    vertex data passed from Python.
*/

in vec3 world_pos;
in vec3 local_pos;
out vec4 FragColor;

uniform vec3 camera_pos;

// DATA UNIFORMS (Direct Arrays)
// We use vec4 because the user is passing "RGBA" data.
uniform vec4 mesh_data[64];
uniform int vertex_count = 64;
uniform float blob_radius = 0.5;

// EFFECT PARAMETERS
uniform float edge_width = 0.1;
uniform vec3 base_color = vec3(0.5, 0.8, 1.0);
uniform vec3 outline_color = vec3(0.0, 0.0, 0.0);

// Map function (The Scene)
float map(vec3 p) {
    float d = 1e10;

    // Iterate through the uniform array directly
    int count = clamp(vertex_count, 0, 64);

    for (int i = 0; i < count; i++) {
        // Use the first 3 components (XYZ) of the RGBA data
        vec3 v = mesh_data[i].xyz;

        float dist_to_vertex = length(p - v) - blob_radius;

        // Smooth union (Metaball effect)
        float k = 0.2;
        float h = clamp(0.5 + 0.5 * (d - dist_to_vertex) / k, 0.0, 1.0);
        d = mix(d, dist_to_vertex, h) - k * h * (1.0 - h);
    }
    return d;
}

void main() {
    vec3 ro = camera_pos;
    vec3 rd = normalize(world_pos - camera_pos);

    float t = 0.0;
    float max_dist = 100.0;
    float last_d = 1e10;

    bool hit = false;
    bool is_edge = false;

    // Raymarching Loop
    for (int i = 0; i < 64; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);

        // Edge Detection
        if (last_d < edge_width && d > last_d + 0.001) {
            is_edge = true;
            break;
        }

        if (d < 0.001) {
            hit = true;
            break;
        }

        last_d = d;
        t += d;
        if (t > max_dist) break;
    }

    // Final Shading
    vec3 final_col;
    if (is_edge) {
        final_col = outline_color;
    } else if (hit) {
        final_col = base_color;
        final_col *= (1.0 - t * 0.02); // Simple distance fog
    } else {
        discard;
    }

    FragColor = vec4(final_col, 1.0);
}
