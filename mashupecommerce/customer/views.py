import uuid
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import *
from django.urls import reverse, reverse_lazy
import razorpay

from adminpannel.models import *
from .froms import *
from django.contrib.auth import *
from django.contrib.auth.decorators import *
from customer.models import *
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def registercustomer(request):
    if request.method == 'POST':
        registerform = RegistrationForm(request.POST)
        if registerform.is_valid():
            username = registerform.cleaned_data['username']
            email = registerform.cleaned_data['emailid']
            firstname = registerform.cleaned_data['firstname']
            lastname = registerform.cleaned_data['lastname']
            password = registerform.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                registerform = RegistrationForm(request.POST)
                context = {'registerform': registerform,
                           'error': 'Username already exists add a new one'}
                return render(request, 'customer/registercustomer.html', context)
            else:
                user = User.objects.create_user(username=username,
                                                email=email,
                                                password=password,
                                                first_name=firstname,
                                                last_name=lastname)
                user.save()
            return HttpResponseRedirect(reverse('logincustomer'))
        else:
            registerform = RegistrationForm(request.POST)
            context = {'registerform': registerform}
            return render(request, 'customer/registercustomer.html', context)
    else:
        registerform = RegistrationForm()
    return render(request, 'customer/registercustomer.html', {'registerform': registerform})


def logincustomer(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('products'))
                else:
                    login_form = LoginForm(request.POST)
                    return render(request, "customer/logincustomer.html", {"form": login_form, "errors": "invalid credtials"})
            else:
                login_form = LoginForm(request.POST)
                print("errors", login_form.errors)
                return render(request, "customer/logincustomer.html", {"form": login_form, "errors": "invalid credtials"})
        else:
            login_form = LoginForm(request.POST)
            return render(request, "customer/logincustomer.html", {"form": login_form, "errors": "invalid credtials"})
    else:
        print("login called")
        login_form = LoginForm()
    return render(request, 'customer/logincustomer.html', {"form": login_form})


@login_required(login_url=reverse_lazy('logincustomer'))
def logoutcustomer(request):
    logout(request)
    return HttpResponseRedirect(reverse('products'))


def homepage(request):
    products = Products.objects.filter(is_active=1)
    usercart = []
    if request.user.is_authenticated:
        usercart = CustomerCart.objects.filter(customer=request.user)
    return render(request, 'customer/products.html', {'products': products, 'usercart': usercart})


@csrf_exempt
@login_required
def addproducttocart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = int(request.POST['product'])
        user = request.user
        cart_instance = CustomerCart(product_id=product_id,
                                     customer=user)
        cart_instance.save()
        success = {
            "result": 'success'
        }
        return JsonResponse(success)


@csrf_exempt
@login_required
def removeproductfromcart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = int(request.POST['product'])
        user = request.user
        cart_instance = CustomerCart.objects.filter(
            customer=user, product=product_id)
        cart_instance.delete()
        return JsonResponse({'result': 'success'})


@login_required(login_url=reverse_lazy('logincustomer'))
def viewcustomercart(request):
    usercart = CustomerCart.objects.filter(
        customer=request.user).select_related('product')
    totalprice = sum(item.product.price for item in usercart)
    checkoutForm = CustomerCheckoutForm()
    return render(request, 'customer/customercart.html', {'usercart': usercart,
                                                          'totalprice': totalprice,
                                                          'checkoutform': checkoutForm})


@login_required(login_url=reverse_lazy('logincustomer'))
def removeproductcartpage(request, cart_item_id):
    user = request.user
    cart_instance = CustomerCart.objects.filter(customer=user, id=cart_item_id)
    cart_instance.delete()
    return HttpResponseRedirect(reverse('viewcustomercart'))


@login_required
def checkoutcustomer(request):
    if request.method == 'POST':
        user = request.user
        address = request.POST['address']
        phone = request.POST['phone']
        usercart = CustomerCart.objects.filter(
            customer=request.user).select_related('product')
        totalprice = sum(item.product.price for item in usercart)
        receipt = str(uuid.uuid1())
        client = razorpay.Client(
            auth=("rzp_test_GTFuHvAaGSPMLI", "2mLX1yz2n1uwAVPoajIpQD39"))
        DATA = {
            'amount': totalprice*100,
            'currency': 'INR',
            'receipt': 'masupreiept',
            'payment_capture': 1,
            'notes': {}
        }
        order_details = client.order.create(data=DATA)
        # return HttpResponse(order_details)
        customercheckout_order_instance = CustomerCheckout(customer=request.user,
                                                           order_id=order_details.get(
                                                               'id'),
                                                           total_amount=totalprice,
                                                           reciept_num=receipt,
                                                           delivery_address=address,
                                                           delivery_phone=phone)
        customercheckout_order_instance.save()
        customercheckout = CustomerCheckout.objects.get(
            id=customercheckout_order_instance.id)
        for item in usercart:
            orderedproduct_instance = customerPayedProducts(customer=request.user,
                                                            product_name=item.product.product_name,
                                                            price=item.product.price,
                                                            product_description=item.product.product_description,
                                                            checkout_details=customercheckout)
            orderedproduct_instance.save()

        context = {'order_id': order_details.get('id'),
                   'amount': totalprice,
                   'amountscript': totalprice*100,
                   'currency': 'INR',
                   'companyname': 'Mashupcommrz',
                   'username': request.user.first_name+' '+request.user.last_name,
                   'useremail': request.user.email,
                   'phonenum': phone,
                   'rzpkey': 'rzp_test_bAYqeZhjXN8pf0'
                   }
        return render(request, 'customer/checkoutform.html', context)
    else:
        return HttpResponseRedirect(reverse('products'))


@csrf_exempt
@login_required(login_url=reverse_lazy('logincustomer'))
def markpaymentsuccess(request):

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.POST['order_id']
        payment_id = request.POST['payment_id']
        payment_signature = request.POST['payment_signature']
        user = request.user
        customercart_order_instance = CustomerCheckout.objects.get(order_id=order_id,
                                                                   customer=user)
        customercart_order_instance.payment_signature = payment_signature
        customercart_order_instance.payment_id = payment_id
        customercart_order_instance.payment_complete = 1
        customercart_order_instance.save()
        customercart_instance = CustomerCart.objects.filter(customer=user)
        customercart_instance.delete()
        return JsonResponse({'result': 'success'})


def viewproductdetails(request, product_id):
    product = Products.objects.filter(id=product_id)
    return render(request, "customer/productdetails.html", {"productdetail": product})


def searchProduct(request):
    data = request.POST["search"]
    product = Products.objects.filter(product_name__icontains=data)
    return render(request, "customer/products.html", {"products": product, "searched": "searched"})


def searchAjax(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products = Products.objects.values_list("product_name", flat=True)
        productList = list(products)
        return JsonResponse(productList, safe=False)
