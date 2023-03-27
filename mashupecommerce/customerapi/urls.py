from customerapi import views
from django.urls import path


urlpatterns = [
    path('registercustomer', views.registercustomer, name='registercustomerapi'),
    path('logincustomer', views.logincustomer, name='logincustomerapi'),
    path('logoutcustomer', views.logoutcustomer, name='logoutcustomerapi'),
    path('listproducts', views.listproducts, name='listproductsapi'),
    path('productdetails', views.productdetails, name='productdetailsapi'),
    path('addproducts', views.addproducts, name="addproductsapi"),
    path("removeproduct", views.removeproducts, name="removeproductsapi"),
    path('listcustomercart', views.listcustomercart, name='listcustomercartapi'),
]
