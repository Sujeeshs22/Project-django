from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import *
from django.contrib.auth.models import User
from django.contrib.auth import *
from rest_framework import status
from rest_framework.permissions import AllowAny
from customerapi.forms import *
from rest_framework.authtoken.models import Token

from adminpannel.models import Products
from customerapi.serializers import *
# Create your views here.


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def registercustomer(request):
    registerform = RegistrationForm(request.data)
    if registerform.is_valid():
        username = registerform.cleaned_data['username']
        email = registerform.cleaned_data['emailid']
        firstname = registerform.cleaned_data['firstname']
        lastname = registerform.cleaned_data['lastname']
        password = registerform.cleaned_data['password']
        if User.objects.filter(username=username).exists():
            registerform = RegistrationForm(request.POST)
            context = {'registerform': registerform.data,
                       'error': 'Username already exists add a new one'}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password,
                                            first_name=firstname,
                                            last_name=lastname)
            user.save()
            context = {'registerform': registerform.data,
                       'success': 'Created user'}
            return Response(context, status=status.HTTP_200_OK)
    else:
        registerform = RegistrationForm(request.POST)
        context = {'registerform': registerform.data,
                   'errors': registerform.errors}
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def logincustomer(request):
    username = request.data.get("username")  # geting the data from the request
    password = request.data.get("password")
    if username is None or password is None:  # checking wether any of the field is empty
        return Response({'error': 'Please provide both username and password'},
                        status=status.HTTP_400_BAD_REQUEST)
    # authenticating a user
    user = authenticate(username=username, password=password)
    if not user:  # unauthenticated user
        return Response({'error': 'Invalid Credentials'},
                        status=status.HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def logoutcustomer(request):
    request.user.auth_token.delete()
    return Response({'message': 'success'}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def listproducts(request):
    products = Products.objects.filter(is_active=1)
    if request.user:
        context = {'userid': request.user.id}

    serializer = ProductsListSerializer(products, many=True, context=context)
    print('serialze', serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def productdetails(request):
    product_id = int(request.data.get("productid"))
    product = Products.objects.get(id=product_id)
    if request.user:
        context = {'userid': request.user.id}
    serializer = ProductsListSerializer(product, context=context)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def addproducts(request):
    product_id = int(request.data.get("product"))
    user = request.user
    usercart = CustomerCart(customer=user, product_id=product_id)
    usercart.save()

    return Response({"result": "success"})


@csrf_exempt
@api_view(["POST"])
def removeproducts(request):
    product_id = int(request.POST["product"])
    user = request.user
    usercart = CustomerCart.objects.filter(
        customer=user, product_id=product_id)
    usercart.delete()
    return Response({"result": "successfully removed product from cart"})


@csrf_exempt
@api_view(["POST"])
def listcustomercart(request):
    usercart = CustomerCart.objects.filter(
        customer=request.user).select_related('product')
    totalprice = sum(item.product.price for item in usercart)
    cartserialized = CustomerCartSerializer(usercart, many=True)
    return Response({'cartitems': cartserialized.data, 'totalprice': totalprice})
