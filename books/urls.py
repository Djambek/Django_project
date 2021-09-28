"""В этом файле описываются все url сайта"""
from django.urls import path
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('', views.home, name='home'), # первая страница, до логина
    path('books_list', views.books_list, name='books_list'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path("<int:id_>/desc/", views.desc, name='desc'),
    path("how_many", views.peoples, name='how_many'),
    path("add_book", views.add_book, name='add_book'),
    url(r'^signup/$', views.signup, name='signup'),
    path('<int:id_>/sure_del/', views.sure_del, name='sure_del'),
    path('<int:id_>/del/', views.del_, name='del'),
    path("profile/", views.profile, name='profile'),
    path("new_book/", views.new_book, name="new_book")
]
urlpatterns += [

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
