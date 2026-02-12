//# This file belongs to S00N's PBNPR Blender Add-on
//# all rights reserved (C) 2024 S00N

// with 'in pos'
void main() {
    // 'pos' is injected as an input by CreateInfo
    gl_Position = vec4(pos, 1.0);
}