
in vec4 vColor;
in vec3 vNormal;
in vec3 point;
in float Depth;

out vec4 fragCol;

void main() {
    // 1. Basic Depth Visualization (Mist effect)
    // Map 0m - 10m range to 0.0 - 1.0 color
    float sceneMaxDist = 10.0;
    float depthMap = clamp(Depth / sceneMaxDist, 0.0, 1.0);
    
    // 2. The Bubble Glow (Fresnel + Depth)
    vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0)); // Simple view dir in view space
    float edge = 1.0 - max(dot(vNormal, viewDir), 0.0);
    edge = pow(edge, 3.0); // Sharp neon edge

    // Result: Darker far away, glowing at the edges
    fragCol = vec4(vColor.rgb * edge, edge);
}