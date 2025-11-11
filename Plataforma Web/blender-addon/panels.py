"""
UI Panels for Blender add-on
"""
import bpy
from bpy.props import StringProperty, IntProperty
from bpy.types import Panel, PropertyGroup


class BIMFM_PT_MainPanel(Panel):
    """Main panel for BIM-FM Platform"""
    bl_label = "BIM-FM Platform"
    bl_idname = "BIMFM_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BIM-FM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.bimfm_props
        
        # API Configuration
        box = layout.box()
        box.label(text="Configuração da API")
        box.prop(props, "api_url")
        box.prop(props, "ifc_file_id")
        
        layout.separator()
        
        # Sync Buttons
        box = layout.box()
        box.label(text="Sincronização")
        
        row = box.row()
        op = row.operator("bimfm.sync_from_platform", text="Carregar da Plataforma")
        op.api_url = props.api_url
        op.ifc_file_id = props.ifc_file_id
        
        row = box.row()
        op = row.operator("bimfm.sync_to_platform", text="Enviar para Plataforma")
        op.api_url = props.api_url
        op.ifc_file_id = props.ifc_file_id
        
        layout.separator()
        
        # Status
        box = layout.box()
        box.label(text="Status")
        if hasattr(props, "last_sync_status"):
            box.label(text=f"Última sincronização: {props.last_sync_status}")


class BIMFM_Properties(PropertyGroup):
    """Properties for BIM-FM add-on"""
    api_url: StringProperty(
        name="API URL",
        default="http://localhost:8000",
        description="URL da API da plataforma web"
    )
    
    ifc_file_id: IntProperty(
        name="IFC File ID",
        default=1,
        min=1,
        description="ID do arquivo IFC na plataforma"
    )
    
    last_sync_status: StringProperty(
        name="Last Sync Status",
        default="Nunca",
        description="Status da última sincronização"
    )


def register():
    bpy.utils.register_class(BIMFM_Properties)
    bpy.utils.register_class(BIMFM_PT_MainPanel)
    bpy.types.Scene.bimfm_props = bpy.props.PointerProperty(type=BIMFM_Properties)


def unregister():
    bpy.utils.unregister_class(BIMFM_PT_MainPanel)
    bpy.utils.unregister_class(BIMFM_Properties)
    del bpy.types.Scene.bimfm_props

