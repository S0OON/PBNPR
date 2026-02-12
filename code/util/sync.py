
import os
import shutil

# Source and destination paths
src = r"E:\soon\projects\PBNPR\code\bpy_glsl_manager"
dst = r"C:\Users\ADMINI~1\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\bpy_glsl_manager"

# Ensure destination exists
os.makedirs(dst, exist_ok=True)

# Iterate through all files and folders in source
for item in os.listdir(src):
    src_path = os.path.join(src, item)
    dst_path = os.path.join(dst, item)

    # If destination already has the file/folder, remove it first (force overwrite)
    if os.path.exists(dst_path):
        if os.path.isfile(dst_path) or os.path.islink(dst_path):
            os.remove(dst_path)
        elif os.path.isdir(dst_path):
            shutil.rmtree(dst_path)

    # Copy file or folder
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dst_path)
    else:
        shutil.copy2(src_path, dst_path)

print("All files copied successfully.")
