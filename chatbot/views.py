from rest_framework import viewsets, status
from .models import UserProfile, Product, Order, ChatSession, ChatMessage
from .serializers import UserProfileSerializer, ProductSerializer, OrderSerializer, ChatSessionSerializer, ChatMessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

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
    @action(methods=['GET'], detail=False)
    def get_out_of_stock_products(self,request):
        result=Product.objects.filter(stock_quantity=0)
        if not result.exists():
            return Response(data={'message':'All products are in stock.'},
                            status=status.HTTP_204_NO_CONTENT)
        #Serialize result
        products=ProductSerializer(result,many=True)
        return Response(products.data,status.HTTP_200_OK)
    @action(methods=['GET'], detail=False,
    url_path='by_name/(?P<name>[^/.]+)'
    )
    def get_products_by_name(self,request, name):
        result=Product.objects.filter(name__icontains=name)
        if not result.exists():
            return Response(data={'message':'No products found with the name '+name},
                            status=status.HTTP_204_NO_CONTENT)
        #Serialize result
        products=ProductSerializer(result,many=True)
        return Response(products.data,status.HTTP_200_OK)
    @action(methods=['get'], detail=False)
    def get_products_price_range(self,request):
        price_min=request.request_parms.get('priceMin')
        price_max=request.request_parms.get('priceMac')
        result=Product.objects.filter(price__gte=price_min, price__lte=price_max)
        #or
        #result=Product.objects.filter(price__range(peice_min,price_max))
        if not result.exists():
            return Response(data={'message':'No products found with the price range '+price_min+' to '+price_max},
                            status=status.HTTP_204_NO_CONTENT)
        #Serialize result
        products=ProductSerializer(result,many=True)
        return Response(products.data,status.HTTP_200_OK)


#CRUD operations for all orders
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer





