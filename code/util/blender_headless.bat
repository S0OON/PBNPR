
cd /d "E:\soon\projects\PBNPR\code\util"

"sync_to_blender.py"

set "A=file.blend"
set "B=E:\soon\projects\PBNPR\resource\examples\blend_mc\scene.blend"


"E:\soon\programs\Blender-5.1\blender.exe" -b %B% --python "blender_headless.py"
