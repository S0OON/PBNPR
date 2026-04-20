import os

from gl_studio.ui.pyside6 import (
    # ,editor_general_template_module_file
    editor_nodeGraph,
    internals,
)


def setup_cube_render_tree():
    """
    Enhanced node tree for rendering a cube:
    - Sets resolution (600x600)
    - Evaluates Camera and Object
    - Adds 'in_vert' resource node for geometry
    - Outputs render to an RGBA Viewer and Printer
    - Nodes are spaced with +50px minimum padding
    """
    graph = editor_nodeGraph.cfg.graph
    if not graph:
        print("❌ Error: Graph not initialized.")
        return

    # Imports
    from gl_studio.examples.nodes.Node_bpy_camData import NODE_CAMERA_EVAL
    from gl_studio.examples.nodes.Node_bpy_object_eval import NODE_OBJECT_EVAL
    from gl_studio.examples.nodes.Node_Dict_join import NODE_DICT_JOIN
    from gl_studio.examples.nodes.Node_Dict_value import NODE_VALUE_DICT
    from gl_studio.examples.nodes.Node_float import NODE_FLOAT
    from gl_studio.examples.nodes.Node_mgl import NODE_MGL_SHADER
    from gl_studio.examples.nodes.Node_printer import NODE_PRINTER
    from gl_studio.examples.nodes.Node_RGBAview import NODE_RGBA_VIEWER
    from gl_studio.examples.nodes.Node_str import NODE_STRING
    from gl_studio.examples.nodes.Node_str_block import NODE_TEXT_BLOCK

    # --- 1. Create Nodes with Spacing Adjustments (+50px) ---
    # Column 0: Input Control (X: -450)
    w_node = graph.create_node(NODE_FLOAT.type_, name="Res Width", pos=[-450, -250])
    h_node = graph.create_node(NODE_FLOAT.type_, name="Res Height", pos=[-450, -100])
    str_cam = graph.create_node(NODE_STRING.type_, name="CamTarget", pos=[-450, 50])
    str_obj = graph.create_node(NODE_STRING.type_, name="ObjTarget", pos=[-450, 200])

    # Column 1: Evaluators & Shaders (X: -150)
    cam_eval = graph.create_node(
        NODE_CAMERA_EVAL.type_, name="BlenderCam", pos=[-150, -50]
    )
    obj_eval = graph.create_node(
        NODE_OBJECT_EVAL.type_, name="BlenderObj", pos=[-150, 200]
    )
    vert_node = graph.create_node(
        NODE_TEXT_BLOCK.type_, name="VertexShader", pos=[-150, 400]
    )
    frag_node = graph.create_node(
        NODE_TEXT_BLOCK.type_, name="FragShader", pos=[-150, 600]
    )

    # Column 2: Packaging Dictionaries (X: 150)
    vd_view = graph.create_node(NODE_VALUE_DICT.type_, name="VD_View", pos=[150, -150])
    vd_proj = graph.create_node(NODE_VALUE_DICT.type_, name="VD_Proj", pos=[150, 0])
    vd_obj = graph.create_node(NODE_VALUE_DICT.type_, name="VD_Obj", pos=[150, 150])
    vd_vert = graph.create_node(
        NODE_VALUE_DICT.type_, name="VD_Vert", pos=[150, 300]
    )  # NEW

    # Column 3: Joiners (X: 450)
    dict_join = graph.create_node(
        NODE_DICT_JOIN.type_, name="UniformJoiner", pos=[450, 50]
    )

    # Column 4: Renderer (X: 750)
    mgl_node = graph.create_node(
        NODE_MGL_SHADER.type_, name="CubeRenderer", pos=[750, 50]
    )

    # Column 5: Output/Feedback (X: 1050)
    rgba_view = graph.create_node(
        NODE_RGBA_VIEWER.type_, name="RGBA View", pos=[1050, -100]
    )
    printer = graph.create_node(NODE_PRINTER.type_, name="Feedback", pos=[1050, 200])

    # --- 2. Configuration ---
    w_node.slider.setValue(600.0)
    h_node.slider.setValue(600.0)
    str_cam.line.setText("active")
    str_obj.line.setText("Cube")

    base_glsl = r"E:\soon\projects\PBNPR\code\addons\gl_studio\examples\opengl"
    vert_node.ui_filepath.setText(os.path.join(base_glsl, "Vdefault.glsl"))
    frag_node.ui_filepath.setText(os.path.join(base_glsl, "Fdefault.glsl"))

    vd_view.line.setText("u_view")
    vd_proj.line.setText("u_proj")
    vd_obj.line.setText("u_model")
    vd_vert.line.setText("in_vert")  # Key for resources

    # --- 3. Connections ---
    # Global Resolutions -> Evaluator, Renderer, and Viewer
    w_node.set_output(0, cam_eval.input(1))
    w_node.set_output(0, mgl_node.input(0))
    w_node.set_output(0, rgba_view.input(1))
    h_node.set_output(0, cam_eval.input(2))
    h_node.set_output(0, mgl_node.input(1))
    h_node.set_output(0, rgba_view.input(2))

    # Blender Evaluation
    str_cam.set_output(0, cam_eval.input(0))
    str_obj.set_output(0, obj_eval.input(0))
    cam_eval.set_output(0, vd_view.input(0))
    cam_eval.set_output(1, vd_proj.input(0))
    obj_eval.set_output(2, vd_obj.input(0))

    # Packaging Uniforms
    vd_view.set_output(0, dict_join.input(0))
    vd_proj.set_output(0, dict_join.input(0))
    vd_obj.set_output(0, dict_join.input(0))

    # Shader Inputs
    dict_join.set_output(0, mgl_node.input(4))  # dict_uni
    vd_vert.set_output(0, mgl_node.input(5))  # dict_res (Input 5)
    vert_node.set_output(0, mgl_node.input(2))
    frag_node.set_output(0, mgl_node.input(3))

    # Visual Output
    mgl_node.set_output(0, rgba_view.input(0))  # Connect Render Map to Viewer
    mgl_node.set_output(0, printer.input(0))

    print(
        "✅ Tree Updated: Spacing increased, 'in_vert' dict added, and RGBA Viewer connected."
    )


def register():
    internals.register()
    editor_nodeGraph.register()
    # editor_general_template_module_file.register()
    # setup_cube_render_tree()


def unregister():
    internals.unregister()
    editor_nodeGraph.unregister()
    # editor_general_template_module_file.unregister()


def check_state():
    a = internals.check_state()
    b = editor_nodeGraph.check_state()
    # c = editor_general_template_module_file.check_state()
    return a and b  # and c


def process_frame():
    internals.process_frame()
    editor_nodeGraph.process_frame()
    # editor_general_template_module_file.process_frame()
