"""
Operators for Blender add-on
"""
import bpy
import requests
import json
from bpy.props import StringProperty, IntProperty, EnumProperty
from bpy.types import Operator


class BIMFM_OT_SyncToPlatform(Operator):
    """Sincronizar dados do Blender para a plataforma web"""
    bl_idname = "bimfm.sync_to_platform"
    bl_label = "Sincronizar para Plataforma"
    bl_options = {'REGISTER', 'UNDO'}

    api_url: StringProperty(
        name="API URL",
        default="http://localhost:8000",
        description="URL da API da plataforma"
    )

    ifc_file_id: IntProperty(
        name="IFC File ID",
        default=1,
        description="ID do arquivo IFC na plataforma"
    )

    def execute(self, context):
        try:
            # Get data from Blender
            blender_data = self.get_blender_data()
            
            # Send to platform
            response = requests.post(
                f"{self.api_url}/api/blender/sync",
                json={
                    "ifc_file_id": self.ifc_file_id,
                    "sync_direction": "from_blender",
                    "blender_data": blender_data
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.report({'INFO'}, "Sincronização concluída com sucesso!")
            else:
                self.report({'ERROR'}, f"Erro na sincronização: {response.text}")
                
        except Exception as e:
            self.report({'ERROR'}, f"Erro: {str(e)}")
        
        return {'FINISHED'}

    def get_blender_data(self):
        """Extract data from Blender scene"""
        data = {
            "assets": []
        }
        
        # Iterate through objects in scene
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                # Get IFC GUID if available (from BlenderBIM)
                ifc_guid = None
                if hasattr(obj, 'BIMObjectProperties'):
                    ifc_guid = getattr(obj.BIMObjectProperties, 'ifc_guid', None)
                
                # Get custom properties
                asset_data = {
                    "ifc_guid": ifc_guid or obj.name,
                    "name": obj.name,
                    "location": {
                        "x": obj.location.x,
                        "y": obj.location.y,
                        "z": obj.location.z
                    }
                }
                
                # Get condition from custom properties
                if "condition_status" in obj:
                    asset_data["condition_status"] = obj["condition_status"]
                if "condition_score" in obj:
                    asset_data["condition_score"] = obj["condition_score"]
                
                data["assets"].append(asset_data)
        
        return data


class BIMFM_OT_SyncFromPlatform(Operator):
    """Sincronizar dados da plataforma web para o Blender"""
    bl_idname = "bimfm.sync_from_platform"
    bl_label = "Sincronizar da Plataforma"
    bl_options = {'REGISTER', 'UNDO'}

    api_url: StringProperty(
        name="API URL",
        default="http://localhost:8000",
        description="URL da API da plataforma"
    )

    ifc_file_id: IntProperty(
        name="IFC File ID",
        default=1,
        description="ID do arquivo IFC na plataforma"
    )

    def execute(self, context):
        try:
            # Get data from platform
            response = requests.get(
                f"{self.api_url}/api/blender/{self.ifc_file_id}/blender-data",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.apply_platform_data(data)
                self.report({'INFO'}, "Dados sincronizados com sucesso!")
            else:
                self.report({'ERROR'}, f"Erro ao obter dados: {response.text}")
                
        except Exception as e:
            self.report({'ERROR'}, f"Erro: {str(e)}")
        
        return {'FINISHED'}

    def apply_platform_data(self, data):
        """Apply platform data to Blender scene"""
        # Update assets based on platform data
        for asset in data.get("assets", []):
            # Find object by IFC GUID or name
            obj = None
            for scene_obj in bpy.context.scene.objects:
                if scene_obj.name == asset.get("name") or \
                   (hasattr(scene_obj, 'BIMObjectProperties') and 
                    getattr(scene_obj.BIMObjectProperties, 'ifc_guid', None) == asset.get("ifc_guid")):
                    obj = scene_obj
                    break
            
            if obj:
                # Update condition properties
                if "condition_status" in asset:
                    obj["condition_status"] = asset["condition_status"]
                if "condition_score" in asset:
                    obj["condition_score"] = asset["condition_score"]
                
                # Update color based on condition
                if asset.get("condition_score"):
                    self.update_object_color(obj, asset["condition_score"])

    def update_object_color(self, obj, condition_score):
        """Update object color based on condition score"""
        color_map = {
            1: (1.0, 0.0, 0.0),  # Red - Critical
            2: (1.0, 0.5, 0.0),  # Orange - Poor
            3: (1.0, 1.0, 0.0),  # Yellow - Fair
            4: (0.0, 1.0, 0.0),  # Green - Good
        }
        
        color = color_map.get(condition_score, (0.5, 0.5, 0.5))
        
        # Create material if needed
        if not obj.data.materials:
            mat = bpy.data.materials.new(name=f"{obj.name}_Material")
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]
        
        mat.use_nodes = True
        if mat.node_tree:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (*color, 1.0)


class BIMFM_OT_SelectAsset(Operator):
    """Selecionar ativo na plataforma"""
    bl_idname = "bimfm.select_asset"
    bl_label = "Selecionar Ativo"
    bl_options = {'REGISTER', 'UNDO'}

    asset_id: IntProperty(
        name="Asset ID",
        description="ID do ativo na plataforma"
    )

    def execute(self, context):
        # Select object in Blender based on asset
        # This would need to match by IFC GUID
        self.report({'INFO'}, f"Selecionando ativo {self.asset_id}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BIMFM_OT_SyncToPlatform)
    bpy.utils.register_class(BIMFM_OT_SyncFromPlatform)
    bpy.utils.register_class(BIMFM_OT_SelectAsset)


def unregister():
    bpy.utils.unregister_class(BIMFM_OT_SyncToPlatform)
    bpy.utils.unregister_class(BIMFM_OT_SyncFromPlatform)
    bpy.utils.unregister_class(BIMFM_OT_SelectAsset)

