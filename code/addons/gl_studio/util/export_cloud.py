from PySide6.QtWidgets import QVBoxLayout
import moderngl as mgl

INSPECTOR:QVBoxLayout
# Ouput nodes list,
# itterated by PAG to evaluate the branches's nodes.
# lifetime is managed by node itself
OUTPUT_NODES = {}
CLOUD_NODES = {}
EXPORT = {}

# moderngl
CTX = mgl.create_context(standalone=True)
CTX.gc_mode = 'context_gc'


