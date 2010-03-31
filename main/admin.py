from django.contrib import admin
from main.models import Department,DataCategory,DepartmentDataCategory,DataSet

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name','abbrev']
    list_display_links = ['name']
    ordering = ['name']

admin.site.register(Department,DepartmentAdmin)

class DataCategoryAdmin(admin.ModelAdmin):
    list_display = ['code','get_type_display','name']
    list_display_links = ['code']
    ordering = ['code']

admin.site.register(DataCategory,DataCategoryAdmin)

class DepartmentDataCategoryAdmin(admin.ModelAdmin):
    list_display = ['dept','category']
    list_display_links = ['category']
    ordering = ['dept']

admin.site.register(DepartmentDataCategory,DepartmentDataCategoryAdmin)

class DataSetAdmin(admin.ModelAdmin):
    list_display = ['category','desc']
    list_display_links = ['desc']

admin.site.register(DataSet,DataSetAdmin)
