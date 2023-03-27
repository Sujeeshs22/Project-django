
from django.conf import settings
from adminpannel import views
from django.urls import path
from django.views.generic.base import RedirectView
from django.conf.urls.static import static


urlpatterns = [
    path('login', views.loginadmin, name='login'),
    path('', RedirectView.as_view(url='login')),
    path('adminlogout', views.logoutadmin, name='adminlogout'),
    path('dashboard', views.admindashboard, name='admindashboard'),
    path('manage-products', views.manageproducts, name='manageproducts'),
    path('add-products', views.addproduct, name="addproducts"),
    path('change-product-status', views.changestatus, name='changestatus'),
    path('edit-product/<int:product_id>',
         views.editproduct, name='editproduct'),
    path("delete-products/<int:product_id>",
         views.deleteproduct, name="deleteproduct"),
    path('manage-users', views.manageusers, name='manageusers'),
    path('change-user-status', views.changestatususer, name='changestatususer'),
    path("delete-user/<int:user_id>", views.deleteuser, name="deleteuser"),
    path("view-user/<int:user_id>", views.viewuser, name="viewuser"),
    path("view-product/<int:product_id>",
         views.viewproduct, name="viewproduct"),
    path('admin-view-reports', views.adminviewreports, name='adminviewreports'),
    path('todayssalesreport', views.todayssalesreport, name='todayssalesreport'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
