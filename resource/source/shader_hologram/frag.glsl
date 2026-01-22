in vec4 vColor;
in float u_time;
out vec4 fragCol;

void main() {
    float scanline = sin((gl_FragCoord.y * 0.8)+u_time) * 0.5 + 0.5;

    vec3 finalRGB = vColor.rgb * scanline;
    
    fragCol = vec4(finalRGB * 2.0, vColor.a * scanline);
}