"""NetMngSys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from NetMngApp import views as NetMngviews
from UserMngApp import views as UserMngviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', UserMngviews.login, name='login'),
    path('base/', NetMngviews.base, name='base'),
    path('devlist/', NetMngviews.devlist, name='devlist'),
    path('devsearch/', NetMngviews.devsearch, name='devsearch'),
    path('crawlinput/', NetMngviews.crawlinput, name='crawlinput'),
    path('crawlnet/', NetMngviews.crawlnet, name='crawlnet'),
    path('datarefresh/', NetMngviews.datarefresh, name='datarefresh'),
    path('nettopology/', NetMngviews.nettopology, name='nettopology'),
    path('SNMPtool/', NetMngviews.SNMPtool, name='SNMPtool'),
    path('devdetail/', NetMngviews.devdetail, name='devdetail'),
    path('devmonitor/', NetMngviews.devmonitor, name='devmonitor'),
    path('settings/', NetMngviews.settings, name='settings'),
    path('deletnet/', NetMngviews.deletnet, name='deletnet'),
    path('test/', NetMngviews.test, name="test")
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
