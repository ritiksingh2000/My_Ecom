from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePage, name='homepage'),
    path('add_cart/<int:id>', AddCart, name='add_cart'),
    path('remove_product/<int:id>', RemoveCart, name='remove_product'),
    path('update_cart/', UpdateCart, name='update_cart'),
    path('add_customer_review', AddCustomerReview, name='add_customer_review'),

    path('products_page/<int:id>', ProductsPage, name='products_page'),
    path('all_products', AllProducts, name='all_products'),
    path('about_us', AboutUs, name='about_us'),
    path('contact_us', ContactUs, name='contact_us'),
    path('product_page/<int:id>', ProductPage, name='product_page'),
    path('serach/', ProductSearch, name='serach'),

    
    path('user/logout/', LogOut, name='logout'),
    path('user/user_login/', UserLogin, name='user_login'),
    path('user/user_signup/', UserSignup, name='user_signup'),
    path('user/my_profile/', UserProfile, name='user_profile'),
    path('user/update_user/', UpdateUser, name="update_user"),


    path('user/become_seller/', BecomeSeller, name="become_seller"),
    path('seller/update_seller_details/', UpdateSellerDetails, name="update_seller_details"),
    path('seller/add_product/', AddProduct, name="add_product"),
    path('seller/update_product/<int:id>', UpdateProduct, name="update_product"),

    path('update_image/', UpdateImage, name="update_image"),


]
