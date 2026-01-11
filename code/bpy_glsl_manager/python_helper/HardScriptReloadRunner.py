import bpy

NAME = "pipeLine.py"
PATH = r"D:\soon\projects\06_pythonShaders\code\pipeLine.py"


if NAME in bpy.data.texts:
    bpy.data.texts.remove(bpy.data.texts[NAME]) 
    
bpy.data.texts.load(PATH) 

exec(bpy.data.texts[NAME].as_string())  