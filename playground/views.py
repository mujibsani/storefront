from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F
from django.db.models.aggregates import Count, Max, Min, Avg, Sum; 
from store.models import Product, OrderItem, Customer, Order, Collection

from django.core.mail import mail_admins, send_mail, BadHeaderError


# Create your views here.
def say_hello(request):
    try:
        send_mail('subject', 'message', 'fromaddress@gmail.com ',['list_of_ricipent_address@gmail.com'])
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': 'protik'})
        # Simple And Operation
        # products = Product.objects.filter( inventory__lt=10).filter(price__lt=20) 
        # And Operation with Q class
        # products = Product.objects.filter(Q(inventory__lt=10) & Q(price__lt=20)) 
        
        # filter using reference collumn name
        # products = Product.objects.filter(inventory=F('collection__id'))
        
        # data sorted Ascending
        # products = Product.objects.order_by('title') 
        
        # data sorted Desending
        # products = Product.objects.order_by('-title') 
        # products = Product.objects.order_by('price','-title').reverse()
        # products = Product.objects.latest('price')
        # products = Product.objects.all()[5:10]
        
        # Inner JOIN and get Values
        # products = Product.objects.values_list('id', 'title', 'collection__title')
        
        # order product list and sorted by title
        # query_set = Product.objects.filter(
        #     id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')
        
        # Deferring Fields. Only mthod so slow for large dataset
        # query_set = Product.objects.only('id', 'title')
        # Now using defer
        # query_set = Product.objects.defer('description')
        
        # select related query
        # query_set = Product.objects.select_related('collection').all()
        
        # prefetch example for using many to many relation
        # query_set = Product.objects.prefetch_related('promotions').select_related('collection').all()
        # query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
        # result = Product.objects.aggregate(Min('price'))
        # query_set = Product.objects.all()
        # list(query_set)
        # collection = Collection(pk=1)
        # collection.title = 'Video Games'
        # collection.featured_product = Product(pk=1)
        # collection.save()
        # Collection.objects.filter(pk=6).update(title='Games')

        


    return render(request, 'hello.html', 
                  {'name': 'protik',  
                   }
                  )