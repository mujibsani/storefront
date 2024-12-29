from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
# from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
# from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly

from .models import Collection, Product, Review, Cart, CartItem, Customer, Order, \
    OrderItem, ProductImage
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializers, \
    CartSerializers, CartItemSerializers, AddCartItemSerializer, UpdateCartItemSerializer,\
        CustomerSerializers, OrderSerializers, CreateOrderSerializers, UpdateOrderSerializer,\
            ProductImageSerializer
from .filters import ProductFilter
from .paginations import DefaultPagination
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission

from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSets(ModelViewSet):
    
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter # Filter Data
    # pagination_class = PageNumberPagination
    pagination_class = DefaultPagination
    search_fields = ['title', 'description'] #, 'collection__title' # Searching Data
    ordering_fields = ['price', 'last_update']
    permission_classes = [IsAdminOrReadOnly]
    
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem.count() > 0:
            return Response({'Product Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSets(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'Collection Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSets(ModelViewSet):
     serializer_class = ReviewSerializers
     
     def get_queryset(self):
         return Review.objects.filter(product_id=self.kwargs['product_pk'])
     
     def get_serializer_context(self):
         return {'product_id': self.kwargs['product_pk']}
 

class CartViewSets(CreateModelMixin,
                  RetrieveModelMixin, 
                  DestroyModelMixin, 
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializers


class CartItemViewSets(ModelViewSet):
    http_method_names = ['get','post','patch', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializers

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects\
            .filter(cart_id=self.kwargs['cart_pk'])\
            .select_related('product')
    
class CustomerViewSets(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    permission_classes = [IsAdminUser]
    
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')
    
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(
            user_id=request.user.id)
        
        if request.method == 'GET':
            serializer = CustomerSerializers(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializers(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
       
       
class OrderViewSets(ModelViewSet):
    http_method_names = ['get','post', 'patch', 'delete', 'head', 'option']
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializers(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializers(order)
        return Response(serializer.data)
        
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializers
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializers
        
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
         
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        
        return Order.objects.filter(customer_id=customer_id)    
       
       
       
class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])       
    
       
       
       
       
       
       
       
       
       
#Class based Generic Views
# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     def get_serializer_context(self):
#         return {'request': self.request}


# class ProductDetails(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
    
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitem.count() > 0:
#             return Response({'Product Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer
#     def get_serializer_context(self):
#         return {'request': self.request}

    
# class CollectionDetails(RetrieveUpdateDestroyAPIView):
#     collection = Collection.objects.annotate(
#         products_count=Count('products')).all()
#     serializer_class = CollectionSerializer
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection, pk=pk)
#         if collection.products.count() > 0:
#             return Response({'Collection Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    

# class CollectionDetails(ListCreateAPIView):
#     pass

# Class Based Views
# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(
#             queryset, many=True, context={'request':request})
#         return Response(serializer.data)
#     def post(self, request):
#         serializer =ProductSerializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class ProductDetails(APIView):
    
#     def get(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     def post(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     def delete(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitem.count() > 0:
#             return Response({'Product Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
# class CollectionList(APIView):
#     def get(self, request):
#         queryset = Collection.objects.annotate(products_count=Count('products'))
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)
#     def post(self, request):
#         serializer =CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class CollectionDetails(APIView):
    
#     def get(self, request, pk):
#         collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count('products')), 
#         pk=pk
#         )
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     def post(self, request, pk):
#         collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count('products')), 
#         pk=pk
#         )
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     def delete(self, request, pk):
#         collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count('products')), 
#         pk=pk
#         )
#         if collection.products.count() > 0:
#             return Response({'Collection Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)




# Function Based views
# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == 'GET':
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(queryset, many=True, context={'request':request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer =ProductSerializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
        
 
# @api_view(['GET','PUT', 'DELETE'])
# def product_details(request, id ):
    
#     product = get_object_or_404(Product, pk=id)
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if product.orderitem.count() > 0:
#             return Response({'Product Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


    
# @api_view(['GET','POST'])
# def collection_list(request):
#     if request.method == 'GET':
#         queryset = Collection.objects.annotate(products_count=Count('products'))
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer =CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)



# @api_view(['GET', 'PUT', 'DELETE'])
# def collection_details(request, pk):
#     collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count('products')), 
#         pk=pk
#         )
#     if request.method == 'GET':
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if collection.products.count() > 0:
#             return Response({'Collection Can not be Deleted. It has been Associated with an order'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    