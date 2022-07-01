from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop.views import IndexView, ItemDetailView, ItemListView, test, create_review, \
add_to_cart, remove_from_cart, CartListView, increase_quantity, decrease_quantity, OrderView, \
make_order

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('<int:pk>/', ItemDetailView.as_view(), name="detail"),
    path('store/', ItemListView.as_view(), name='item_list'),
    path('cart/', CartListView.as_view(), name='cart'),
    path('order/', OrderView.as_view(), name='order'),
    

    path('create_review/<int:id>/', create_review, name="create_review"),
    path('add_to_cart/<int:pk>/', add_to_cart, name="add_to_cart"),
    path('remove_from_cart/<int:id>/', remove_from_cart, name="remove_from_cart"),
    path('increase_quantity/<int:id>/', increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:id>/', decrease_quantity, name='decrease_quantity'),
    path('make_order/', make_order, name="make_order"),



    path('test/', test, name="test"),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

