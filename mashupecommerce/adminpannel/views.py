import csv
import datetime
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from adminpannel.models import Products
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from customer.models import *


def loginadmin(request):
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse('admindashboard'))
    # else:
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            useradmin = authenticate(username=username, password=password)

            if useradmin is not None:
                if useradmin.is_active and useradmin.is_superuser:
                    login(request, useradmin)
                    return HttpResponseRedirect(reverse('admindashboard'))
                else:
                    login_form = LoginForm(request.POST)
                    return render(request, "adminpannel/login.html", {"form": login_form, "error": "Access denied"})
            else:
                login_form = LoginForm(request.POST)
                return render(request, "adminpannel/login.html", {"form": login_form, "error": "The Account does not exists"})
        else:
            login_form = LoginForm()
            return render(request, "adminpannel/login.html", {"form": login_form})
    else:
        login_form = LoginForm()
    return render(request, 'adminpannel/login.html', {"form": login_form})


def checksuperuser(useradmin):
    return useradmin.is_superuser


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def logoutadmin(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def admindashboard(request):
    return render(request, 'adminpannel/admindashboard.html', {})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def manageproducts(request):
    product = Products.objects.all()
    return render(request, "adminpannel/manageproducts.html", {"products": product})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def addproduct(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_name = product_form.cleaned_data['product_name']
            product_description = product_form.cleaned_data['product_description']
            price = product_form.cleaned_data['price']
            product_image = request.FILES['product_image']

            product_instance = Products(product_name=product_name,
                                        product_description=product_description,
                                        price=price,
                                        product_picture=product_image)
            product_instance.save()
            return HttpResponseRedirect(reverse('manageproducts'))
        else:
            product_form = ProductForm(request.POST, request.FILES)
            return render(request, 'adminpannel/addproducts.html', {'productform': product_form})
    else:
        product_form = ProductForm()
        return render(request, 'adminpannel/addproducts.html', {'productform': product_form})


@csrf_exempt
@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def changestatus(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = int(request.POST['product'])
        action = request.POST['action']
        product_instance = Products.objects.get(id=product_id)
        if action == "disable":
            product_instance.is_active = 0
        else:
            product_instance.is_active = 1
        product_instance.save()
        return JsonResponse({'result': 'success'})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def editproduct(request, product_id):

    if request.method == 'POST':
        product_form = EditProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_name = product_form.cleaned_data['product_name']
            product_description = product_form.cleaned_data['product_description']
            price = product_form.cleaned_data['price']

            product_instance = Products.objects.get(id=product_id)
            product_instance.product_name = product_name
            product_instance.product_description = product_description
            product_instance.price = price
            if request.FILES:
                product_image = request.FILES['product_image']
                product_instance.product_picture = product_image
            product_instance.save()
            return HttpResponseRedirect(reverse('manageproducts'))
        else:
            product_form = EditProductForm(request.POST, request.FILES)
            return render(request, 'adminpannel/editproduct.html', {'productform': product_form})
    else:
        product_instance = Products.objects.get(id=product_id)
        product_form = EditProductForm(initial={'product_name': product_instance.product_name,
                                                'product_description': product_instance.product_description,
                                                'price': product_instance.price,
                                                'product_image': product_instance.product_picture
                                                })
        return render(request, 'adminpannel/editproduct.html', {'productform': product_form, 'current_image': product_instance.product_picture})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def deleteproduct(request, product_id):
    product_instance = Products.objects.get(id=product_id)
    product_instance.delete()
    return HttpResponseRedirect(reverse('manageproducts'))


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def manageusers(request):
    users = User.objects.filter(is_superuser=0, is_staff=0)
    return render(request, 'adminpannel/manageusers.html', {'users': users})


@csrf_exempt
@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def changestatususer(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        action = request.POST['action']
        user_id = int(request.POST['user_id'])
        user_instance = User.objects.get(id=user_id)
        if action == "disable":
            user_instance.is_active = 0
        else:
            user_instance.is_active = 1
        user_instance.save()
        return JsonResponse({'result': 'success'})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def deleteuser(request, userId):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        useradmin = User.objects.get(id=userId)
        useradmin.delete()
        return HttpResponseRedirect(reverse("manageusers"))


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def viewuser(request, user_id):
    user_instance = User.objects.get(id=user_id)
    orders = customerPayedProducts.objects.filter(
        customer=user_id, checkout_details__payment_complete=1)
    return render(request, "adminpannel/userview.html", {"useradmin": user_instance, 'orders': orders})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def viewproduct(request, product_id):
    product_instance = Products.objects.get(id=product_id)
    return render(request, "adminpannel/viewproduct.html",
                  {"product": product_instance})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def adminviewreports(request):
    return render(request, 'adminpannel/adminreports.html', {})


@user_passes_test(checksuperuser, login_url=reverse_lazy('login'))
def todayssalesreport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="salesreport"' + \
        str(datetime.date.today())+'".csv"'
    writer = csv.writer(response)
    today_min = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(
        datetime.date.today(), datetime.time.max)
    sales = CustomerCheckout.objects.filter(
        payedon__range=(today_min, today_max))
    writer.writerow(['Order_id', 'Payment_id', 'Amount',
                    'Reciept', 'Phonenum', 'Address'])
    for sale in sales:
        writer.writerow([sale.order_id, sale.payment_id, sale.total_amount,
                        sale.reciept_num, sale.delivery_phone, sale.delivery_address])
    return response
