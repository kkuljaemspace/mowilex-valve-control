from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import VendorURL, ItemMap, ScanTable, EpicorPO, ValveOperation, MappingValve, ValveSet, ModbusConfig


# Resource dan Admin untuk VendorURL
class VendorURLResource(resources.ModelResource):
    class Meta:
        model = VendorURL

@admin.register(VendorURL)
class VendorURLAdmin(ImportExportModelAdmin):
    resource_class = VendorURLResource
    list_display = ('vendor_id', 'uri', 'ssl', 'format_output', 'created_date')
    search_fields = ('uri',)

# Resource dan Admin untuk ItemMap
class ItemMapResource(resources.ModelResource):
    class Meta:
        model = ItemMap

@admin.register(ItemMap)
class ItemMapAdmin(ImportExportModelAdmin):
    resource_class = ItemMapResource
    list_display = ('item_map_id', 'vendor', 'internal_item_id', 'external_item_id', 'created_by', 'created_date')
    search_fields = ('internal_item_id', 'external_item_id', 'created_by')

# Resource dan Admin untuk ScanTable
class ScanTableResource(resources.ModelResource):
    class Meta:
        model = ScanTable

@admin.register(ScanTable)
class ScanTableAdmin(ImportExportModelAdmin):
    resource_class = ScanTableResource
    list_display = ('tag_id', 'trans_date', 'vendor', 'vehicle_no', 'item', 'po', 'um', 'weighbridge', 'silo_qty', 'error_by', 'plc_command', 'created_date')
    search_fields = ('vehicle_no', 'item', 'po', 'um')

# Resource dan Admin untuk EpicorPO
class EpicorPOResource(resources.ModelResource):
    class Meta:
        model = EpicorPO

@admin.register(EpicorPO)
class EpicorPOAdmin(ImportExportModelAdmin):
    resource_class = EpicorPOResource
    list_display = ('ponum', 'created_at', 'updated_at')
    search_fields = ('ponum',)

# Resource dan Admin untuk ValveOperation
class ValveOperationResource(resources.ModelResource):
    class Meta:
        model = ValveOperation

@admin.register(ValveOperation)
class ValveOperationAdmin(ImportExportModelAdmin):
    resource_class = ValveOperationResource
    list_display = ('valve_number', 'command_value', 'status_value', 'status', 'created_at')
    search_fields = ('valve_number', 'status')

# Resource dan Admin untuk ValveOperation
class ValveSetResource(resources.ModelResource):
    class Meta:
        model = ValveSet

@admin.register(ValveSet)
class ValveSetAdmin(ImportExportModelAdmin):
    resource_class = ValveSetResource
    list_display = ('valve_number', 'status', 'updated_at')
    search_fields = ('valve_number', 'status')


# Resource dan Admin untuk ValveOperation
class MappingValveOperationResource(resources.ModelResource):
    class Meta:
        model = MappingValve

@admin.register(MappingValve)
class MappingValveOperationAdmin(ImportExportModelAdmin):
    resource_class = MappingValveOperationResource
    list_display = ('valve_number', 'part_number', 'status_value_number', 'created_at')
    search_fields = ('valve_number', 'part_number')


# Resource dan Admin untuk ModbusConfig
class ModbusConfigResource(resources.ModelResource):
    class Meta:
        model = ModbusConfig

@admin.register(ModbusConfig)
class ModbusConfigAdmin(ImportExportModelAdmin):
    resource_class = ModbusConfigResource
    list_display = ('android_ip', 'android_port', 'plc_ip', 'plc_port', 'auto_start', 'updated_at')
    search_fields = ('android_ip', 'plc_ip')
    readonly_fields = ('updated_at', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

