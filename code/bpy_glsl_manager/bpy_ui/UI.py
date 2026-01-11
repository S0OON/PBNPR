import bpy


class Tab(bpy.types.Panel):
    # ... bl_ attributes ...

    def draw(self, context):
        layout = self.layout
        
        # Create a "Search/Add" style menu
        col = layout.column(align=True)
        col.label(text="Add New Effect:")
        
        # Dynamically create buttons for every registered shader
        for shader_name in bpy.gl.descs.keys():
            op = col.operator("glsl.add_block", text=shader_name, icon='NODE_SEL')
            op.shader_type = shader_name # This passes the name to the operator!

        layout.separator()
        
        # Draw the existing stack
        for i, item in enumerate(context.scene.gl_blockStack):
            box = layout.box()
            header = box.row()
            header.label(text=item.name, icon='SHADING_RENDERED')
            
            # Get the specific description for this instance
            desc = bpy.gl.descs.get(item.shader_type)
            
            if desc and "UI_Spec" in desc:
                # If your ShaderDesc has a specific draw function or class
                # You can call a custom draw function here to show specific sliders
                col = box.column()
                col.prop(item, "intensity") 
                if item.shader_type == "DEFAULT":
                    col.prop(item, "target_obj") # Only show for paint!

#----------- OP -----------------
class TAB_add(bpy.types.Operator):
    bl_idname = "glsl.add_block"
    bl_label = "Add Shader Block"
    
    # This variable captures which shader was picked
    shader_type: bpy.props.StringProperty() 

    def execute(self, context):
        stack = context.scene.gl_blockStack
        new_block = stack.add()
        
        # Set the type based on what was passed from the UI
        new_block.shader_type = self.shader_type
        new_block.name = self.shader_type.title()
        
        return {'FINISHED'}

class TAB_RemoveBlock(bpy.types.Operator):

    bl_idname = "glsl.remove_block"
    bl_label = "Remove Block"
    index: bpy.props.IntProperty() # Which one to delete
    
    def execute(self, context):
        # Remove item at specific index
        context.scene.gl_blockStack.remove(self.index)
        return {'FINISHED'}

# -----------------------------------------

class Template_Block(bpy.types.PropertyGroup):
    # 1. Which shader logic to use? (Points to your 'Shader_desc')
    shader_type: bpy.props.EnumProperty(
            name="Type",
            items=[
                ('PAINT', "Paint Shader", ""),
                ('SIMPLE', "Simple Circle", ""),
            ]
        )
    
    # 2. Shared Parameters (Exposed in UI)
    intensity: bpy.props.FloatProperty(name="Intensity", default=1.0)
    target_obj: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    # UI expects `is_active` and `name` so expose them here
    is_active: bpy.props.BoolProperty(name="Active", default=True)
    name: bpy.props.StringProperty(name="Name", default="Block")

# ----------------------------------
classes = (Template_Block, TAB_add, TAB_RemoveBlock, Tab)
UI_classes = []

def register():
    # 1. Collect all UI classes from your shader descs
    # We use a set to avoid registering the same class twice if multiple shaders use it
    unique_ui_classes = set()
    for desc in getattr(bpy, "gl_descs", {}).items():
        if hasattr(desc, "UI_DATA"):
            unique_ui_classes.add(desc.UI_DATA)


    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Class {cls} already registered or failed: {e}")
        
    # 3. Register Shader-Specific PropertyGroups
    for cls in unique_ui_classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Class {cls} already registered: {e}")
    
    # 4. CRITICAL: The CollectionProperty needs a type. 
    # Use the first one or a generic base class. 
    bpy.types.Scene.gl_blockStack = bpy.props.CollectionProperty(type=Template_Block)

def unregister():
    for cls in reversed(tuple(UI_classes)):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    if hasattr(bpy.types.Scene, "gl_blockStack"):
        del bpy.types.Scene.gl_blockStack

