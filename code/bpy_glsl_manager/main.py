

def main():
    import sys
    project_root = r"D:\soon\projects\PBNPR\code\bpy_glsl_manager"

    if project_root not in sys.path:
        sys.path.append(project_root)
    
    from src import init_containers as LOADER
    import importlib
    from bpy_ui import ui_tab as UI
    
    modules= [LOADER,UI]
    for mod in modules:
        importlib.reload(mod)

    LOADER.reload_shaders()
    UI.unregister()
    UI.register()

if __name__ == "__main__":
    main()
