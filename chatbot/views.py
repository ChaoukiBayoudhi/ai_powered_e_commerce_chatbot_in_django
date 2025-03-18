from rest_framework import viewsets
from .models import UserProfile, Product, Order, ChatSession, ChatMessage
from .serializers import UserProfileSerializer, ProductSerializer, OrderSerializer, ChatSessionSerializer, ChatMessageSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

#implement CRUD (Create, Read/Retreive, Update, Delete) operations for Product model
#ModelViewSet provides 6 default functions for CRUD operations
#list() - Retrieve all objects (products)
#retrieve() - Retrieve an object by id
#create() - Create an object (insert a new product)
#update() - Complete Update an object by id (update an existing product)
#partial_update() - Partial Update an object by id (update an existing product partially)
#destroy() - Delete an object by id


class ProductViewSet(viewsets.ModelViewSet):
    #CRUD operations for all products
    queryset = Product.objects.all()
    #CRUD operations for products with price greater than 1000
    #queryset = Product.objects.filter(price__gt=1000)
    serializer_class = ProductSerializer

#CRUD operations for all orders
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer





class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
