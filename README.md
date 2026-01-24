# PBNPR

Physically based non-photorealistic rendering. (WIP)
> methods for artists to fill their needs with 100% control like an ASM project.

## 1.GLSL manager
> ### TLDR: Modifiers tab but with user defined GLSL shaders!

![How to use the addon](/resource/img/UI_guide.png)
[Or watch this Video instead](https://x.com/S00N28202269/status/2015151274149241310?s=20)
no TLDR: it Provides the ability to load custom shaders writtin in OpenGL or simply Facilitates GLSL usage;
By providing a standard translation unit that the addon understands to store/load/bake the shader instructions with a simple UI.

Ultimate customizability. Ultimate performance.

for developers: One pholosophy used here is that any .py has the same access when ever, and thus the cusomizablilty is all up to you, like even spawining a cube middle of registeration, who cares!
 + Another phOlosphy here is the DESCRIPTION data class, its a contract to register your shader instructions in, aka target edit.
 
 + Another phOlosophy is KISS technology, "KISS (Keep It Simple, Stupid) to Hardware phOlosophy." (i made that up)

how to use:

+ load the addon 'bpy_gl_manager.zip' -> view 3d (N-Menu) -> PBNPR -> GLSL manager,

+ you have 2 buttons, one provides you with an folder containing an empty shader so you can directly start writing the shader, after you're done you can then store in in the other button 'import' 


FEATURES:
As said, true GLSL! in two ways mainly:

1.As said, Custom shaders!  

+ meaning user defined/GPU source code

+ an 'shader block' can contain paramters you would want to control in the scene via frames, drivers ..etc2
  
+ managerd via instances, multiple shader types, multiplied executed shaders!
                            
2.As said, storing and baking!, in a texture for any later use (in compositor/materail/exernal).
