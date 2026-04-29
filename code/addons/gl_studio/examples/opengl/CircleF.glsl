#version 330

in vec2 UV;

out vec4 fragCol;

uniform vec2 resolution;


void main(){

vec3 circle = vec3(distance(UV,vec2(0.5,0.5)));

fragCol=vec4(vec3(circle),1.0);
}
