from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from . import views
from rest_framework_nested  import routers

# router = routers.DefaultRouter()
# router.register('products', views.ProductViewSet)
# router.register('collections', views.CollectionViewSets)



# router = SimpleRouter()
router = routers.DefaultRouter()
router.register('products', views.ProductViewSets, basename='product')
router.register('collections', views.CollectionViewSets)
router.register('carts', views.CartViewSets)
router.register('customers', views.CustomerViewSets)
router.register('orders', views.OrderViewSets, basename='orders')

product_router = routers.NestedSimpleRouter(router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSets, basename='product-reviews')
product_router.register('images', views.ProductImageViewSet, basename='product-images')
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSets, basename='cart-items')

#URL Config
urlpatterns = router.urls + product_router.urls + cart_router.urls


# urlpatterns = [
# #     path('products/', views.product_list),
# #     path('products/<int:id>/', views.product_details),
# #     path('collections/', views.collection_list),
# #     path('collections/<int:pk>/', views.collection_details, name='collection-detail'),

# #These are class based views
#     # path('products/', views.ProductList.as_view()),
#     # path('products/<int:pk>/', views.ProductDetails.as_view()),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>/', views.CollectionDetails.as_view(), name='collection-detail'),
# ]
