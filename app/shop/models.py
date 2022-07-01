from django.db import models
import math
from datetime import datetime, timedelta

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to = "category_image")

    def get_count(self):
        count = 0
        items = Item.objects.filter(category=self)
        for item in items:
            color_qty = ColorItemQuantity.objects.filter(item=item)
            for qty in color_qty:
                count += qty.quantity
        return count


    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to ='brands', null=True, blank=True)

    def __str__(self):
        return self.name

    def get_count(self):
        count = 0
        items = Item.objects.filter(brand=self)
        for item in items:
            color_qty = ColorItemQuantity.objects.filter(item=item)
            for qty in color_qty:
                count += qty.quantity
        return count




class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    main_image = models.ImageField(upload_to ='item_main_image')
    date_add = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.name
    
    def get_discount_percentage(self):
        percentage = (self.price - self.discount_price)/self.price * 100
        return math.ceil(percentage)
    
    def is_new(self):
        return self.date_add > datetime.now().date() - timedelta(days=14)
            



class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="item_image")

    def __str__(self):
        return f'картинка - {self.item.name}'

class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class ColorItemQuantity(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.color.name} - {self.item.name}'


class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    text = models.TextField()
    rating = models.IntegerField()
    date_add = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['item', 'email']

    def __str__(self):
        return f'{self.name} - {self.rating}'

class Cart(models.Model):
    item = models.ForeignKey(ColorItemQuantity, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    session_key = models.CharField(max_length=255)
    ordered = models.BooleanField(default=False)

    # class Meta:
    #     unique_together = ['item', 'session_key', 'ordered']


    def __str__(self):
        return f'Товар {self.item.item.name} - {self.quantity} количестве'


    def get_price(self):
        if self.item.item.discount_price:
            return self.item.item.discount_price
        return self.item.item.price

    def get_final_price(self):
        return self.get_price() * self.quantity
    


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=15)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Заказ № {self.id} товар {self.cart.item.item.name} по адресу {self.address}'
