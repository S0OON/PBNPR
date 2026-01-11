import importlib

def main():
    from src import shaders_embedding as GPU
    from bpy_ui import UI
    lib = [GPU,UI]
    for l in lib: importlib.reload(l)

    GPU.Reload()
    UI.register()

if __name__ == "__main__":
    main()