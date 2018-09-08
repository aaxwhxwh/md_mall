from django.contrib import admin
from celery_tasks.html.tasks import generate_static_list_html

# Register your models here.
from goods import models

class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        generate_static_list_html.delay()

    def delete_model(self, request, obj):
        obj.delete()
        generate_static_list_html.delay()


class GoodChannelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_list_html.delay()

    def delete_model(self, request, obj):
        obj.delete()
        generate_static_list_html.delay()


admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
