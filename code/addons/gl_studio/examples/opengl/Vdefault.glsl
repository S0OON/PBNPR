#version 330

uniform mat4 mOBJ;
uniform mat4 mVIEW;
uniform mat4 mPROJ;

in vec3 in_vert;

void main() {
    gl_Position = mPROJ * mVIEW * mOBJ * vec4(in_vert, 1.0);
}
