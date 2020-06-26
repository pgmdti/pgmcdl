"""pgmcdl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from pgm import views

urlpatterns = [
    path('', views.index, name="index"),
    path('upload/', views.upload, name="upload"),
    path('uploadprocs/', views.uploadprocs, name="uploadprocs"),
    path('cdas/all/', views.tableall, name="cdas_all"),
    path('cdas/remessa/', views.remessacdl, name="remessacdl"),
    path('search/', views.search, name="search_cpfcnpj"),
    path('filter/1/', views.filterone, name="filter_one"),
    path('cdas/antigas/sintetico/', views.cdasantigas1, name="cdas_antigas1"),
    path('cdas/antigas/analitico/', views.cdasantigas2, name="cdas_antigas2"),
    path('cdas/cep/valida/', views.validacep, name="valida_cep"),
    path('detail/<idcda>', views.cdadetail, name="cdadetail"),
    path('cdascontribuinte/<doc>', views.cdascontribuinte, name="cdascontribuinte"),
    path('remessa/download/<idremessa>', views.downloadremessa, name="download_remessa"),
    path('remessa/listar/', views.listaremessas, name="listar_remessas"),
    path('success/', views.success, name="success"),
    path('admin/', admin.site.urls),
]
