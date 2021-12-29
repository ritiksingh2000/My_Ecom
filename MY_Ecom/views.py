from django.contrib.messages.api import add_message, error
from django.core.checks import messages
from django.shortcuts import render, redirect
from django.utils.functional import empty
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.messages import info
from django.contrib.auth.hashers import make_password
import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
import random
from twilio.rest import Client

# Create your views here.
"""
HOMEPAGE
"""

def HomePage(request):
    pp = "static/Profile_img/download.png"
    cart = None
    items = 0
    customer_review = Customer_Review.objects.all()
    if request.user.is_authenticated == True:
        user = User.objects.get(id=request.user.id)
        
        if Customer.objects.filter(User=request.user.id).exists():
            user = Customer.objects.get(User=request.user.id)
            pp = f"{user.User_Img}"
        else:
            user = User.objects.get(id=request.user.id)
            customer_create = Customer.objects.create(User=user, User_Img="static/Profile_img/download.png")
            customer_create.save()
            user_address = User_Address.objects.create(User=user)
            user_address.save()
            return redirect("homepage")
    
        
        category = Category.objects.all()
        product = Product.objects.all()
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        if request.user.is_authenticated: 
            if UserCart.objects.filter(User=user).exists():
                cart = UserCart.objects.all().filter(User=user)
            else:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                    cart = GuestCart.objects.all().filter(IP=ip)
        return render(request, 'Home.html', {"pp":pp, "cart":cart, "customer":customer, "items":items, "category":category, "product":product, "customer_review":customer_review})
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        if GuestCart.objects.filter(IP=ip).exists():
            cart = GuestCart.objects.all().filter(IP=ip)
            items = GuestCart.objects.all().filter(IP=ip).count()
        else:
            cart = 0

        category = Category.objects.all()
        product = Product.objects.all()
        return render(request, 'Home.html', {"cart":cart, "items":items, "product":product, "category":category, "customer_review":customer_review})


def LogOut(request):
    logout(request)
    info(request, "User Loggedout")
    return redirect("homepage")


def UserLogin(request):
    user_email = request.POST['email']
    password = request.POST['password']

    user = User.objects.filter(email=user_email)
    if user.exists():
        user = User.objects.get(email=user_email)
        username =  user.username
        auth = authenticate(request, username=username, password=password)
        if auth is not None:
            login(request, auth)  
            info(request, "Loggedin Successfully")
        else:
            info(request, "Wrong Password. Please Try Again")
    else:
        info(request, "Email Doesn't Exist.")
    return redirect("homepage")


def UserSignup(request):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['pass']
    c_pass = request.POST['c_pass']

    if password == c_pass:
        user_email = User.objects.filter(email=email)
        user_username = User.objects.filter(username=username)
        if user_email.exists():
            info(request, "Email You Entered is Alredy in Use.")
        else:
            if user_username.exists():
                info(request, "Username you entered is alredy in use. Please try another Username.")
            else:
                password = make_password(password)
                Add_User =User.objects.create(first_name=first_name,last_name=last_name, email=email, username=username, password=password)
                Add_User.save()
                info(request, "Account Created Successfully Created. Please Login.")
    else:
        info(request, "Passowrds did'nt match. Please Try Again")

    return redirect("homepage")



"""
USER PROFILE PAGE
"""

def UserProfile(request):
    if request.user.is_authenticated == True:
        cart = None
        verified = False
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        is_address = User_Address.objects.filter(User=user)
        address = None
        
        category = Category.objects.all()

        if Seller.objects.all().filter(User=user):
            seller = Seller.objects.get(User=user)
        else:
            seller=None

        is_product = Product.objects.filter(Seller=seller)
        if is_product.exists():
            product = Product.objects.all().filter(Seller=seller)
        else:
            product = None

        is_order = Order.objects.filter(To=request.user.email).exists()
        if is_order == True:
            order = Order.objects.all().filter(To=request.user.email)
            odr_product = OrderProduct.objects.all()
        else:
            order = None
            odr_product = None

        

        if is_address is not None:
            is_address = True
            address = User_Address.objects.get(User=user)
        else:
            is_address = False

        if customer.e_verify == 1 and customer.p_verify == 1:
            verified = "🟢"
        else:
            verified = "🔴"
        pp = customer.User_Img
        if request.user.is_authenticated: 
            if UserCart.objects.filter(User=user).exists():
                cart = UserCart.objects.all().filter(User=user)
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                cart = GuestCart.objects.all().filter(IP=ip)
        return render(request, "profile.html", {"verified":verified, "customer":customer, "is_address":is_address, "address":address, "order":order, "seller":seller,"odr_product":odr_product, "pp":pp, "product":product, "category":category, "cart":cart})
    
    else:
        info(request, "Please Login To Access Profile.")
        return redirect('homepage')

def UpdateUser(request):
    user = User.objects.get(id=request.user.id)
    address = User_Address.objects.get(User=user)
    customer = Customer.objects.get(User=user)

    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    username = request.POST['username']
    Address = request.POST['address']
    country = request.POST['Country']
    state = request.POST['State']
    pincode = request.POST['Pincode']

    address.Address = Address 
    address.Country = country
    address.State = state 
    address.Pincode = pincode
    address.save()
    
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.username = username
    user.save()

    customer.save()
    
    info(request, "User Prodile Updated Successfully.")
    return redirect("user_profile")

def BecomeSeller(request):
    user = User.objects.get(id=request.user.id)
    customer = Customer.objects.get(User=user)
    user_adderss = User_Address.objects.get(User=user)

    seller_logo = request.FILES['seller_logo']
    seller_name = request.POST['seller_name']
    seller_email = request.POST['seller_email']
    seller_phno = request.POST['seller_ph']
    seller_address = request.POST['seller_address'] 
    seller_state = request.POST['seller_state']
    seller_country = request.POST['seller_country']
    seller_pincode = request.POST['seller_pincode']

    seller = Seller.objects.create(User=user, Business_Logo=seller_logo, Seller_Name=seller_name, Seller_PhoneNo=seller_phno, Seller_Email=seller_email, Address=seller_address, Country=seller_country, State=seller_state, Pincode=seller_pincode)
    seller.save()
    customer.is_seller = 1
    customer.save()

    info(request, "You are a seller now.")
    return redirect('user_profile')


def UpdateSellerDetails(request):
    user = User.objects.get(id=request.user.id)
    seller = Seller.objects.get(User=user)

    name = request.POST['seller_name']
    email = request.POST['seller_email']
    phone = request.POST['seller_phno']
    logo = request.FILES['seller_logo']
    address = request.POST['address']
    state = request.POST['state']
    country = request.POST['country']
    pincode = request.POST['pincode']
    print(logo)

    seller.Seller_Name = name
    seller.Seller_Email = email
    seller.Business_Logo = logo
    seller.Seller_PhoneNo = phone
    seller.Address = address
    seller.Country = country
    seller.State = state
    seller.Pincode = pincode
    seller.save()
    info(request, "Seller Details Updated Successfully")

    return redirect("user_profile")

def AddProduct(request):
    user = User.objects.get(id=request.user.id)
    seller = Seller.objects.get(User=user)
    Image = request.FILES['image']
    name = request.POST['name']
    category = Category.objects.get(id=request.POST['category'])
    price = int(request.POST['price'])
    discount = int(request.POST['d_price'])

    desc = request.POST['desc']
    stock = int(request.POST['stock'])
    q = int(request.POST['q'])
        
    product = Product.objects.create(Image=Image, Seller=seller, Name=name, Category=category, Desc=desc, Price=price, in_stock=stock, Discount=discount, Stock=q )
    product.save()

    info(request, f"You have created {name} Product Successfully.")

    return redirect("user_profile")


def UpdateProduct(request, id):
    
    name = request.POST['name']
    category = Category.objects.get(id=int(request.POST['category']))
    price = int(request.POST['price'])
    discount = int(request.POST['d_price'])
    
    desc = request.POST['desc']
    stock = int(request.POST['stock'])
    q = int(request.POST['q'])
    
    product = Product.objects.get(id=id)
    product.Name = name
    product.Category = category
    product.Desc = desc
    product.Price = price
    product.Stock = q
    product.Discount = discount
    product.in_stock = stock
    product.save()

    info(request, f"You have Update {name} Product Successfully.")

    return redirect("user_profile")

def UpdateImage(request):
    of = request.POST['of']
    if of == "user":
        user = User.objects.get(id=int(request.user.id))
        customer = Customer.objects.get(User=user)
        customer.User_Img = request.FILES['image']
        customer.save()
        info(request, "User Profile Image Updated.")
    elif of == "seller":
        seller = Seller.objects.get(id=int(request.POST['id']))
        seller.Business_Logo = request.FILES['image']
        seller.save()
        info(request, "Your Logo is Updated.")
    elif of == "product":
        product = Product.objects.get(id=int(request.POST['id']))
        product.Image = request.FILES['image']
        product.save()
        info(request, "The Product image is Updated.")
    else:
        info(request, "Unable To Update image Pleage Try Again") 

    return redirect("user_profile")


def AddCart(request, id):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        product_id = id
        product = Product.objects.get(id=product_id)
        price = int(product.Price)
        discount = int(product.Discount)
        if UserCart.objects.filter(User=user, Product=product).exists():
            if product.Discount == 0:
                p_price =product.Price
            else:
                p_price =product.Discount
                
            cart = UserCart.objects.get(User=user, Product=product)
            cart.Quantity = int(cart.Quantity)+1
            cart.Price = int(p_price)*int(cart.Quantity)
            cart.Discount = int(cart.Discount)*int(cart.Quantity)
            cart.save()
        else:
            addtocart = UserCart.objects.create(User=user, Product=product, Price=price, Discount=discount)
            addtocart.save()
        info(request, f"{product.Name} is added to cart.")

    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        product_id = id
        product = Product.objects.get(id=product_id)
        price = int(product.Price)
        discount = int(product.Discount)
        if GuestCart.objects.filter(IP=ip, Product=product).exists():
            
            cart = GuestCart.objects.get(IP=ip, Product=product)
            cart.Quantity = int(cart.Quantity)+1
            cart.Price = int(product.Price)*int(cart.Quantity)
            cart.Discount = int(product.Discount)*int(cart.Quantity)
            cart.save()
        else:
            addtocart = GuestCart.objects.create(IP=ip, Product=product, Price=price, Discount=discount)
            addtocart.save()
        info(request, f"{product.Name} is added to cart.")

    return redirect('homepage') 

def AddCustomerReview(request):
    name = request.POST['name']
    about = request.POST['about']
    star = int(request.POST['stars'])
    review = request.POST['review']

    def repeat_string(a_string, target_length):
        number_of_repeats = target_length // len(a_string) + 1
        a_string_repeated = a_string * number_of_repeats
        a_string_repeated_to_target = a_string_repeated[:target_length]
        return a_string_repeated_to_target
    stars = repeat_string("⭐",star)

    if len(name) == 0:
        review = Customer_Review.objects.create(About=about, Stars=stars, Review=review)
        
    else:
        review = Customer_Review.objects.create(FullName=name, About=about, Stars=stars, Review=review)
        
    review.save()
    info(request, "Review Added Successfully")
    return redirect("homepage")

def RemoveCart(request, id):
    product = Product.objects.get(id=int(request.GET['p_id']))
    if request.user.is_authenticated:
        cart_product = UserCart.objects.get(id=id, Product=product)
        cart_product.delete()
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        cart_product = GuestCart.objects.get(IP=ip, Product=product)
        cart_product.delete()
    info(request, "Product Was Removed From Cart")
    return redirect("homepage")

def AddProductQty(request):
    product_id = request.GET['product_id']
    cart_id = request.GET['cart_id']
    product = Product.objects.get(id=int(product_id))
    if request.user.is_authenticated:
        cart = UserCart.objects.get(id=int(cart_id), Product=product)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')        
        cart = GuestCart.objects.get(IP=ip, Product=product)
    
    cart.Quantity = cart.Quantity+1
    cart.Price = int(product.Price)*int(cart.Quantity)
    cart.Discount = int(product.Discount)*int(cart.Quantity)

    if cart.Quantity > 0:
        cart.save()
    else:
        cart.delete()
    info(request, "Product Increased")

    return redirect("homepage")

def SubProductQty(request):
    product_id = request.GET['product_id']
    cart_id = request.GET['cart_id']
    product = Product.objects.get(id=int(product_id))
    if request.user.is_authenticated:
        cart = UserCart.objects.get(id=int(cart_id), Product=product)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')        
        cart = GuestCart.objects.get(IP=ip, Product=product)

            
    cart.Quantity = cart.Quantity-1
    cart.Price = int(product.Price)*int(cart.Quantity)
    cart.Discount = int(product.Discount)*int(cart.Quantity)

    if cart.Quantity > 0:
        cart.save()
        info(request, "Product Reduced")
    else:
        cart.delete()
        info(request, "Product Deleted")
    

    return redirect("homepage")


def ProductsPage(request, id):
    cart = None
    pp = "static/Profile_img/download.png"
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    categories = Category.objects.get(id=id)
    category = Category.objects.all()
    products = Product.objects.all().filter(Category=categories)
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)

    return render(request, "products.html", {"products":products, "category":category, "categories":categories, "pp":pp, "cart":cart})

def AllProducts(request):
    cart = None

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    products = Product.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)

    return render(request, "AllProducts.html", {"products":products, "category":category, "pp":pp, "cart":cart})

def AboutUs(request):
    cart = None

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)


    about = AboutMyEcom.objects.get(id=1)

    return render(request, "AboutUs.html", {"category":category, "pp":pp, "cart":cart, "about":about})

def QueryMessage(request):
    if request.method == "POST":
        name = request.POST['fullname']
        email = request.POST['email']
        about = request.POST['about']
        message = request.POST['message']
        contact_message = ContactUs.objects.create(FullName=name, About=about, Email=email, Body=message)
        #To customer
        send_mail(
            f"Your Message Is Recived | My_Ecom ",
            f"We Recived Your Message About:{about}\n\n We will resposnd as fast as possible.",
            os.environ['Gmail_Host_Email'],
            [email],
            fail_silently=True,
        )
        #To Owner
        send_mail(
            f"{about} | From : {name}",
            message,
            os.environ['Gmail_Host_Email'],
            [os.environ['Gmail_Host_Email']],
            fail_silently=True,
        )
        contact_message.save()
        info(request, "Message Sent Successfully.")

    else:
        info(request, "Unable to send message. Please Try Again")
    return redirect("contact_us")


def Contact_Us(request):
    cart = None
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)


    return render(request, "ContactUs.html", {"category":category, "pp":pp, "cart":cart})


def ProductPage(request, id):
    cart = None
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)
    
    product = Product.objects.get(id=id)
    if int(product.Discount) == 0:
        order = int(product.Price)
    else:
        order = int(product.Discount)
    products = Product.objects.all().exclude(id=int(product.id))

    return render(request, "Product_Page.html", {"category":category, "order":order, "pp":pp, "cart":cart, "product":product, "products":products})

def ProductSearch(request):
    if request.method == 'POST':    
        cart = None
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            customer = Customer.objects.get(User=user)
            pp = f"{customer.User_Img}"
        else:
            pp = "static/Profile_img/download.png"
        category = Category.objects.all()
        if request.user.is_authenticated: 
            if UserCart.objects.filter(User=user).exists():
                cart = UserCart.objects.all().filter(User=user)
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                cart = GuestCart.objects.all().filter(IP=ip)

        search_term = request.POST['search'].capitalize()
        print(search_term)
        products = Product.objects.all()
        
        return render(request, "Search.html", {"category":category, "pp":pp, "cart":cart, "search_term":search_term, "products":products})

    else:
        return redirect("homepage")

    
def BuyProduct(request, id):
    cart = None
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
        address = User_Address.objects.get(User=request.user)
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)

    product = Product.objects.get(id=id)
    order_id = f"ODR-{datetime.datetime.now()}".replace(" ","")
    if product.Discount ==0 :
        odr_amount = product.Price
    else:
        odr_amount = product.Discount
    
    Discount = round(((int(product.Price)-int(product.Discount))/int(product.Price))*100)
    Discount_Amount = int((Discount/100)*product.Price )
    
    if request.user.is_authenticated:
        return render(request, "BuyProduct.html", {"category":category, "pp":pp, "cart":cart, "product":product, "odr_amount":odr_amount, "order_id":order_id, "Discount":Discount, "address":address, "customer":customer, "Discount_Amount":Discount_Amount})
    else:
        return render(request, "BuyProduct.html", {"category":category, "pp":pp, "cart":cart, "product":product, "odr_amount":odr_amount, "order_id":order_id, "Discount":Discount, "Discount_Amount":Discount_Amount})

def CartCheckout(request):
    cart = None
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
        address = User_Address.objects.get(User=request.user)
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)

    order_id = f"ODR-{datetime.datetime.now()}".replace(" ","")
        
    if request.user.is_authenticated:
        odr_cart = UserCart.objects.all().filter(User=user)
        items = sum(odr_cart.values_list("Quantity", flat=True))
        print(items)
        
        odr_price = sum(odr_cart.values_list("Price", flat=True))
        odr_amount = sum(odr_cart.values_list("Discount", flat=True))
        odr_discount = int(odr_price-odr_amount)
        print(odr_amount)
        
        
    
        
        return render(request, "Checkout.html", {"category":category, "pp":pp, "cart":cart, "odr_cart":odr_cart, "odr_amount":odr_amount, "odr_price":odr_price, "odr_discount":odr_discount ,"items":items, "order_id":order_id,  "address":address, "customer":customer})
    else:
        odr_cart = GuestCart.objects.all().filter(IP=ip)
        items = sum(odr_cart.values_list("Quantity", flat=True))
        print(items)
        
        odr_price = sum(odr_cart.values_list("Price", flat=True))
        odr_discount = sum(odr_cart.values_list("Discount", flat=True))
        odr_amount = int((odr_price+odr_discount)/100)
        print(odr_amount)
        
        
        return render(request, "Checkout.html", {"category":category, "pp":pp, "cart":cart, "odr_cart":odr_cart, "odr_amount":odr_amount, "odr_price":odr_price, "odr_discount":odr_discount ,"items":items, "order_id":order_id})

def MakePayment(request):
    if request.method == "POST":
        cart = None
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            customer = Customer.objects.get(User=user)
            pp = f"{customer.User_Img}"
        else:
            pp = "static/Profile_img/download.png"
        category = Category.objects.all()
        if request.user.is_authenticated: 
            if UserCart.objects.filter(User=user).exists():
                cart = UserCart.objects.all().filter(User=user)
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                cart = GuestCart.objects.all().filter(IP=ip)

    
        if request.POST['type'] == "product_payment":
            type = "product_payment"
            p_id = int(request.POST['p_id'])
            product = Product.objects.get(id=p_id)
            Amount = request.POST['odr_amount']
            order_id = request.POST['order_id']
            seller = Seller.objects.get(id=int(product.Seller.id))
            address = f"{request.POST['address']} , {request.POST['state']}, {request.POST['country']}, {request.POST['pincode']}"
            status = OrderStatus.objects.get(id=1)
            phoneno = str(request.POST['phone'])
            email = str(request.POST['email'])
            first_name = str(request.POST['first_name'])
            last_name = str(request.POST['last_name'])

            order_product = OrderProduct.objects.create(OrderNumber=order_id, Quantity=1, Amount=Amount, Product=product)
            order_product.save()
            create_order = Order.objects.get_or_create(OrderNumber=order_id, First_Name=first_name , Last_Name=last_name, PhoneNo=phoneno, From=seller, To=email , Amount=Amount, Address=address, Status=status)
            
            product.Stock = int(product.Stock)-1
            product.save()
            
            return render(request, "PaymentPage.html",{"category":category, "pp":pp, "cart":cart, "product":product, "odr_amount":Amount, "order_id":order_id, "type":type})
        
        elif request.POST['type'] == "cart_checkout":
            type = "cart_checkout"
            Amount = request.POST['odr_amount']
            order_id = request.POST['order_id']
            address = f"{request.POST['address']} , {request.POST['state']}, {request.POST['country']}, {request.POST['pincode']}"
            status = OrderStatus.objects.get(id=1)
            phoneno = str(request.POST['phone'])
            email = str(request.POST['email'])
            first_name = str(request.POST['first_name'])
            last_name = str(request.POST['last_name'])
            items = sum(cart.values_list("Quantity", flat=True))
            
            for i in cart:
                if i.Discount == 0:
                    p_price = i.Price
                else:
                    p_price = i.Discount
                product = i.Product
                product.Stock = int(product.Stock)-1
                product.save()
                seller = Seller.objects.get(id=int(product.Seller.id))
                Quantity = i.Quantity
                Product_Amount = p_price
                order_product = OrderProduct.objects.create(OrderNumber=order_id, Quantity=Quantity, Amount=Product_Amount, Product=product)
                order_product.save()
            
            create_order = Order.objects.get_or_create(OrderNumber=order_id, First_Name=first_name , Last_Name=last_name, PhoneNo=phoneno, From=seller, To=email , Amount=Amount, Address=address, Status=status)
            
            
            
            return render(request, "PaymentPage.html",{"category":category, "pp":pp, "cart":cart, "product":product, "odr_amount":Amount, "order_id":order_id,"items":items, "type":type})
        else:
            info(request, "Server Error Please Try Again.")
            return redirect("homepage")
            
    else:
        info(request, "Some Error Occured. Please Try Again")
        return redirect("homepage")
    
def OrderSuccessfull(request,order_id):
    cart = None
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)

    order=Order.objects.get(OrderNumber=order_id)
    order.Status = OrderStatus.objects.get(id=2)
    order.PaymentStatus = 1
    order.save()
    order_product = OrderProduct.objects.filter(OrderNumber=order_id)
    print(order_product)
    items = order_product.count()
    
    if items <= 1:
        order_product = OrderProduct.objects.get(OrderNumber=order_id)
    else:
        order_product = OrderProduct.objects.all().filter(OrderNumber=order_id)
    
    seller = order.From.Seller_Email
    from_email = "business.ritiksingh@gmail.com"
    to = str(order.To) 
    subject = "Order Confirmation From My Ecom"
    message = render_to_string(template_name="email.html", context={"order":order, "order_product":order_product, 'items':items} )
    plain_message = strip_tags(message)
    
    send_mail(subject, plain_message, from_email, [to], html_message=message, fail_silently=True)

    return render(request, "OrderSuccessfull.html", {"category":category, "pp":pp, "cart":cart})


def Verify(request):
    cart = None
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        customer = Customer.objects.get(User=user)
        pp = f"{customer.User_Img}"
    else:
        pp = "static/Profile_img/download.png"
    category = Category.objects.all()
    if request.user.is_authenticated: 
        if UserCart.objects.filter(User=user).exists():
            cart = UserCart.objects.all().filter(User=user)
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            cart = GuestCart.objects.all().filter(IP=ip)
            
    PhoneNo = request.POST['PhoneNo']
    OTP = random.randrange(100000,999999)
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                body=f'Hi there, Your 6-Digit My Ecom Phone Number Verification OTP is {OTP}',
                                from_='+12086034813',
                                to=f'+91{PhoneNo}'
                            )
    info(request, "A OTP was generated and sent to your mobile number.")

    return render(request, "Verify.html", {"category":category, "pp":pp, "cart":cart, "OTP":OTP, "PhoneNo":PhoneNo})


def VerifyOTP(request):
    if request.method == "POST":
        OTP = request.POST['OTP']
        otp =request.POST['otp']
        if otp == OTP:
            user = User.objects.get(id=request.user.id)
            customer = Customer.objects.get(User=user)
            customer.p_verify = 1
            customer.Phone_No = request.POST['PhoneNo']
            customer.save()
            info(request, "Phone Number Verified. Please Verify Your Email Also.")
            return redirect("user_profile")
        else:
            info(request, "Wrong OTP. ")
        
    else:
        info(request, "Unable to verify. Please try again.")
    return redirect("phone_verification")
    
def VerifyEmail(request):
    import socket
    if request.method == 'POST':
        url = f"{request.get_host()}/verify_user_email/verification?verify={request.user.id}&set_verification=true"
        s_to = str(request.POST['email'])
        about = f"To verify {request.user.first_name} {request.user.last_name}'s My Ecom Account"
        body = f"To Verify your My Ecom Email Please click the link bellow: \n\n\n\n {url}"
        send_mail(
            about,
            body,
            os.environ['Gmail_Host_Email'],
            [s_to],
            fail_silently=True,
        )
        info(request, "An Email is sent to verify. ")
    else : 
        info(request, "Unable to send email at this moment. Please try again later")
    return redirect("user_profile")

def VerifyEmailURL(request):
    user = User.objects.get(id=int(request.GET['verify']))
    customer = Customer.objects.get(User=user)
    customer.e_verify = 1
    customer.save()
    info(request, "Email Verification Completed.")
    
    return redirect("user_profile")

def UpdateOrderPayment(request, id):
    
    order = Order.objects.get(id=id)
    OS = OrderStatus.objects.get(id=2)
    order.PaymentStatus = 1
    order.Status = OS
    order.save()
    order_product = OrderProduct.objects.filter(OrderNumber=order.OrderNumber)
    print(order_product)
    items = order_product.count()
    
    if items <= 1:
        order_product = OrderProduct.objects.get(OrderNumber=order.OrderNumber)
    else:
        order_product = OrderProduct.objects.all().filter(OrderNumber=order.OrderNumber)
    seller = order.From.Seller_Email
    from_email = "business.ritiksingh@gmail.com"
    to = str(order.To) 
    subject = "Order Confirmation From My Ecom"
    message = render_to_string(template_name="email.html", context={"order":order, "order_product":order_product, 'items':items} )
    plain_message = strip_tags(message)
    
    send_mail(subject, plain_message, from_email, [to], html_message=message, fail_silently=True)
    
    info(request, f"Order:{order.OrderNumber} Has Paid For the Order.")
    
    return redirect("user_profile")

def UpdateOrderStatus(request, id):
    
    ocs = int(request.GET['ocs'])
    if ocs == 2:
        order = Order.objects.get(id=id)
        OS = OrderStatus.objects.get(id=3)
        order.Status = OS
        order.save()
        info(request, f"Order:{order.OrderNumber} Is SuccessFully Shipped")
    
    if ocs == 3:
        order = Order.objects.get(id=id)
        OS = OrderStatus.objects.get(id=4)
        order.Status = OS
        order.save()
        info(request, f"Order:{order.OrderNumber} Is SuccessFully Delivered")
    
    return redirect("user_profile")