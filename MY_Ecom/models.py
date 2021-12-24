from django.contrib.admin.options import StackedInline
from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields import BLANK_CHOICE_DASH
from PIL import Image
from ckeditor.fields import RichTextField

class Customer(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    User_Img = models.ImageField(null=True, upload_to='upload/Profile_img')
    Phone_No = models.CharField(max_length=100, null=True)
    e_verify = models.BooleanField(default=0)
    p_verify = models.BooleanField(default=0)
    is_seller = models.BooleanField(default=0)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if self.e_verify == 1 and self.p_verify == 1:
            verified = "✔"
        else:
            verified = "❌"
        return f"{self.User} | {verified}"

class User_Address(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Address = models.CharField(max_length=200, null=True, default="Your location", blank=True)
    Country = models.CharField(max_length=100, null=True, default="Your location", blank=True)
    State = models.CharField(max_length=100, null=True, default="Your location", blank=True)
    Pincode = models.CharField(max_length=100, null=True, default="Your location", blank=True)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.User}"



class Seller(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Business_Logo = models.ImageField(upload_to="upload/seller/logo", default="upload/seller/logo/default_logo.png")
    Seller_Name = models.CharField(max_length=200, null=True)
    Seller_PhoneNo = models.CharField(max_length=200, null=True)
    Seller_Email = models.CharField(max_length=200, null=True)
    Address = models.CharField(max_length=200, null=True)
    Country = models.CharField(max_length=100, null=True)
    State = models.CharField(max_length=100, null=True)
    Pincode = models.CharField(max_length=100, null=True)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.Seller_Name} | {self.Seller_Email} | {self.Country}"



class Category(models.Model):
    Image = models.ImageField(null=True, upload_to="upload/category_img/", blank=True)
    Name = models.CharField(max_length=100, null=True)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.Name
   

class Product(models.Model):
    Seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100, null=True)
    Image = models.ImageField(null=True, upload_to="upload/product_img/")
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    Desc = models.TextField(null=True)
    Price = models.IntegerField(null=True)
    Stock = models.CharField(max_length=120, null=True)
    Discount = models.IntegerField(null=True)
    in_stock = models.BooleanField(default=0)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if self.in_stock == 1:
            active = "🟢"
        else:
            active = "🔴"
        return f"{self.Name} | {self.Price} | {active}"
    
    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.Image.path)
        width, height = img.size  # Get dimensions

        if width > 300 and height > 400:
            # keep ratio but shrink down
            img.thumbnail((width, height))

        # check which one is smaller
        if height < width:
            # make square by cutting off equal amounts left and right
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
            img = img.crop((left, top, right, bottom))

        elif width < height:
            # make square by cutting off bottom
            left = 0
            right = width
            top = 0
            bottom = width
            img = img.crop((left, top, right, bottom))

        if width > 300 and height > 400:
            img.thumbnail((300, 400))

        img.save(self.Image.path)



class Product_Review(models.Model):
    Username = models.CharField(max_length=150, null=True)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    About = models.CharField(max_length=150, null=True)
    Review = models.TextField()
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.Username} | {self.About}"


class Customer_Review(models.Model):
    FullName = models.CharField(default='A Customer', max_length=150)
    About = models.CharField(max_length=150, null=True)
    Stars = models.CharField(max_length=5, default="⭐⭐⭐⭐⭐")
    Review = models.TextField()
    Date = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.FullName} | {self.About}"


class OrderStatus(models.Model):
    Name = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return self.Name

class OrderProduct(models.Model):
    OrderNumber = models.CharField(max_length=100, null=True)    
    Quantity =models.CharField(max_length=200, null=True, blank=True, default=1)
    Amount = models.CharField(max_length=100, null=True, blank=True)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Date = models.DateField(auto_now_add=True) 
    
    def __str__(self) -> str:
        return f"{self.OrderNumber} | {self.Product}"


class Order(models.Model):
    OrderNumber = models.CharField(max_length=100, null=True)
    First_Name = models.CharField(max_length=100, null=True, blank=True)
    Last_Name = models.CharField(max_length=100, null=True, blank=True)
    PhoneNo = models.CharField(max_length=100, null=True, blank=True)
    From = models.ForeignKey(Seller, on_delete=models.CASCADE)
    To = models.CharField(max_length=100, null=True, blank=True)
    Amount = models.CharField(max_length=100, null=True, blank=True)
    Product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE)
    Address = models.CharField(max_length=200, null=True, blank=True)
    OrderDate = models.DateTimeField(auto_now_add=True)
    Status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    PaymentStatus = models.BooleanField(default=0)
    

    def __str__(self) -> str:
        if self.PaymentStatus == 1:
            PaymentStatus = "🟢"
        else:
            PaymentStatus = "🔴"
        return f"{self.To} | {self.From} | {self.Status} | {PaymentStatus}"

class UserCart(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Price = models.IntegerField()    
    Discount = models.IntegerField()
    Quantity = models.IntegerField(default=1, null=True)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.User} | {self.Product}"

class GuestCart(models.Model):
    IP = models.CharField(max_length=200, null=True, blank=True)
    Price = models.IntegerField()    
    Discount = models.IntegerField()
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=1, null=True)
    Date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.IP} | {self.Product}"

class AboutMyEcom(models.Model):
    CompanyName = models.CharField(max_length=100, null=True,blank=True)
    Body = RichTextField()
    Date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.CompanyName} | {self.Date}"

class ContactUs(models.Model):
    FullName = models.CharField(max_length=100, null=True, blank=True)
    About = models.CharField(max_length=200, null=True, blank=True)
    Email = models.CharField(max_length=100, null=True, blank=True)
    Body = RichTextField()
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.FullName} | {self.About} | {self.Date}"
