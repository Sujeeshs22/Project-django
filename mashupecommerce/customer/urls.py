from django.urls import path
from customer import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
urlpatterns = [
    path('', RedirectView.as_view(url='products')),
    path('registercustomer', views.registercustomer, name='registercustomer'),
    path('logout', views.logoutcustomer, name='logoutcustomer'),
    path('logincustomer', views.logincustomer, name='logincustomer'),
    path('products', views.homepage, name='products'),
    path('addtocart', views.addproducttocart, name='addtocart'),
    path('removefromcart', views.removeproductfromcart, name='removefromcart'),
    path('viewcustomercart', views.viewcustomercart, name='viewcustomercart'),
    path('removefromcartpage/<int:cart_item_id>',
         views.removeproductcartpage, name='removeproductcartpage'),
    path('checkoutcustomer', views.checkoutcustomer, name='checkoutcustomer'),
    path('markpaymentsuccess', views.markpaymentsuccess, name='markpaymentsuccess'),
    path("viewproduct-details/<int:product_id>",
         views.viewproductdetails, name="viewproductdetails"),
    path("searchproduct", views.searchProduct, name="searchproduct"),
    path('searchAjax', views.searchAjax, name="searchAjax")
]
