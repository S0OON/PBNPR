

def main():
    import sys
    project_root = r"D:\soon\projects\PBNPR\code\bpy_VFR"

    if project_root not in sys.path:
        sys.path.append(project_root)

    from ui import ui
    ui.register()
    return


if __name__ == '__main__':
    main()