import os
import subprocess

# Mutes the debugpy frozen modules warning
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

# 1. Change directory
util_dir = r"E:\soon\projects\PBNPR\code\util"
os.chdir(util_dir)

# 2. Run sync_to_blender.py
print("Running sync_to_blender.py...")
subprocess.run(["python", "sync_to_blender.py"], check=True)

# 3. Set environment variables
os.environ["A"] = "file.blend"
b_path = r"E:\soon\projects\PBNPR\resource\examples\blend_mc\scene.blend"
os.environ["B"] = b_path

# 4. Run Blender headless
blender_exe = r"E:\soon\programs\Blender-5.1\blender.exe"
print("Launching Blender headless...")


# We use b_path directly instead of querying the OS environment variable string
subprocess.run([blender_exe, "-b", b_path, "--python", "blender_headless.py"], check=True)