from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from .models import Item, Category, ItemImage, Color, ColorItemQuantity, Brand, Review, Cart, Order
import telegram_send 
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q


class IndexView(ListView):
    model = Item
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    
class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = ItemImage.objects.filter(item=self.get_object())
        context['colors'] = ColorItemQuantity.objects.filter(item = self.get_object())
        context['related_items'] = Item.objects.filter(category=self.get_object().category)
        reviews = Review.objects.filter(item=self.get_object())
        context['reviews'] = reviews

        rating_list = []

        for rating in reviews.values_list('rating'):
            rating_list.append(rating[0])


        rating_dict = {}

        for i in range(1, 6):
            rating_dict[f'rating_{i}'] = rating_list.count(i)

        
        try:
            avg = round(sum(rating_list) / len(rating_list), 1)
        except ZeroDivisionError:
            avg = 0
        rating_dict['avg'] = avg
        rating_len = len(rating_list)
        rating_dict['rating_len'] = rating_len

        context['rating_dict'] = rating_dict
        return context

class ItemListView(ListView):
    model = Item
    template_name = "store.html"
    paginate_by = 2

    def get_queryset(self):
        queryset = self.model.objects.all()
        price_min = self.request.GET.get("price-min")
        price_max = self.request.GET.get("price-max")
        single_category = self.request.GET.get('single-category')
        name = self.request.GET.get("name")
        if single_category:
            if single_category != "0":
                queryset=queryset.filter(category__id = single_category)
            if name:
                queryset=queryset.filter(name__icontains=name)

        if price_min and price_max:
            queryset = queryset.filter(price__gt=price_min, price__lte=price_max)
            category_ids = []
            brands_ids = []

            for name in self.request.GET.keys():
                if name.startswith('category'):
                    category_ids.append(int(name.split('-')[1]))
                elif name.startswith('brand'):
                    brands_ids.append(int(name.split('-')[1]))
            if category_ids:
                    queryset = queryset.filter(category__in=category_ids)
            if brands_ids:
                    queryset = queryset.filter(brand__in=brands_ids)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()

        return context


class CartListView(ListView):
    model = Cart
    template_name = 'cart.html'


class OrderView(TemplateView):
    template_name = "checkout.html"

def make_order(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    address = request.POST.get('address')
    phone_number = request.POST.get('tel')
    notes = request.POST.get('notes')

    messages = []

    
    carts = Cart.objects.filter(session_key = request.session.session_key, ordered=False)

    for cart in carts:
        if cart.quantity != 0:
            new_order = Order(name=name, 
            email=email, 
            address=address, 
            phone_number=phone_number, notes=notes, cart=cart)

            cart.item.quantity -= cart.quantity
            cart.item.save()

            new_order.save()
            cart.ordered = True
            cart.save()

            messages.append(f'')
    if messages:
        messages.insert(0, f'Товар {cart.item.item.name} в количестве {cart.quantity} \
        по стоимости {cart.get_price()}, итого в сумме {cart.get_final_price()}')
        telegram_send.send(messages=messages)
        return HttpResponseRedirect(reverse('index'))


def create_review(request, id):
    if request.method == "POST":
        item = Item.objects.get(id=id)
        name = request.POST.get('name')
        email = request.POST.get('email')
        text = request.POST.get('text')
        rating = request.POST.get('rating')

        new_review = Review(name=name, email=email, text=text, rating=int(rating), item=item)
        new_review.save()

        return redirect('detail', pk=id)

        #Review.objects.create()


def add_to_cart(request, pk):
    main_item = get_object_or_404(Item, pk=pk)
    print(main_item)

    color_id = request.GET.get("color")
    quantity = request.GET.get("quantity") if request.GET.get("quantity") else 1

    session_key = request.session.session_key
    if color_id:
        item = get_object_or_404(ColorItemQuantity, id=color_id)
    else:
        item = ColorItemQuantity.objects.filter(item=main_item, quantity__gt=0)[0]
    try:
        cart = Cart.objects.get(session_key = request.session.session_key, ordered=False, item=item)
    except ObjectDoesNotExist as e:
        cart = Cart(item=item, quantity=quantity, session_key=session_key)
    else:
        cart.quantity += int(quantity)
        messages.add_message(request, messages.SUCCESS, 'Товар успешно добавлен')
    finally:
        cart.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_cart(request, id):
    cart = get_object_or_404(Cart, id=id)
    cart.delete()
    messages.add_message(request, messages.SUCCESS, 'Товар успешно удален')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def increase_quantity(request, id):
    cart = get_object_or_404(Cart, id=id)
    cart.quantity += 1
    if cart.quantity > cart.item.quantity:
        cart.quantity = cart.item.quantity
    cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def decrease_quantity(request, id):
    cart = get_object_or_404(Cart, id=id)
    cart.quantity -= 1
    if cart.quantity < 0:
        cart.quantity = 0
    cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



def test(request):
    print(request.GET)
    return HttpResponse("OK")




