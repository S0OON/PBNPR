

def main():
    import sys
    import importlib
    project_root = r"D:\soon\projects\PBNPR\code\bpy_glsl_manager"

    if project_root not in sys.path:
        sys.path.append(project_root)
    
    from bpy_gl import GLSLbase
    from bpy_ui import ui_tab as UI
    
    modules= [
        GLSLbase,
        UI
    ]
    for mod in modules:
        importlib.reload(mod)

    GLSLbase.register()
    UI.register()

if __name__ == "__main__":
    main()
