
import shutil
import os
from pathlib import Path

# Define paths
REPO_SOURCE = r"E:\soon\projects\PBNPR\code\glsl_manager"
BLENDER_DEST = r"C:\Users\ADMINI~1\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\glsl_manager"

def sync_to_blender():
    """Sync bpy_glsl_manager from repo to Blender addons (forced overwrite)"""
    
    # Verify source exists
    if not os.path.exists(REPO_SOURCE):
        print(f"❌ ERROR: Source directory not found: {REPO_SOURCE}")
        return False
    
    # Verify destination exists
    if not os.path.exists(BLENDER_DEST):
        os.makedirs(BLENDER_DEST)
    
    try:
        # Remove existing destination
        if os.path.exists(BLENDER_DEST):
            print(f"🗑️  Removing existing directory: {BLENDER_DEST}")
            shutil.rmtree(BLENDER_DEST)
        
        # Copy entire directory
        print(f"📋 Copying from: {REPO_SOURCE}")
        print(f"📍 Copying to:   {BLENDER_DEST}")
        shutil.copytree(REPO_SOURCE, BLENDER_DEST)
        
        print("✅ SUCCESS: Files synced to Blender addons!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR during sync: {e}")
        return False

if __name__ == "__main__":
    sync_to_blender()
