from django.contrib import admin, messages
from django.db.models.aggregates import Count

from django.utils.html import format_html, urlencode
from django.urls import reverse

from . import models

# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name='inventory'
    
    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
    

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']
    
    def thumbnail(self, instace):
        if instace.image.name != '':
            return format_html(f'<img src="{instace.image.url}" class="thumbnail">')
        return 
    
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    search_fields = ['title']
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display = ['title', 'price', 'inventory_status', 'collection_title']
    list_editable = ['price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
     
    def collection_title(self, product):
        return product.collection.title
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} product successfully Updated.',
            messages.ERROR
        )
    
    class Media:
        css = {
            'all': ['store/styles.css']
        }


@admin.register(models.Customer)   
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class orderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0
    

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields=['customer']
    inlines = [orderItemInline]
    list_display = ['id', 'placed_at', 'customer']
    


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']
    
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        
        url = (reverse('admin:store_product_changelist') 
               + '?'
               + urlencode({
                   'collection__id':str(collection.id)
               }))
        return format_html('<a href="{}">{}</a>',url, collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('products')
        )