"""
BIM-FM Platform Blender Add-on
Sincronização bidirecional entre Blender e a plataforma web
Compatível com BlenderBIM/Bonsai
"""

bl_info = {
    "name": "BIM-FM Platform Sync",
    "author": "BIM-FM Platform",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > BIM-FM",
    "description": "Sincronização bidirecional com plataforma BIM-FM",
    "category": "Import-Export",
}

import bpy
from . import operators
from . import panels

def register():
    operators.register()
    panels.register()

def unregister():
    operators.unregister()
    panels.unregister()

if __name__ == "__main__":
    register()

