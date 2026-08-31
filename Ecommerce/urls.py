from django.contrib import admin
from django.urls import include, path


urlpatterns = [

    # =====================================================
    # ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls
    ),


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "accounts/",
        include("django.contrib.auth.urls")
    ),


    # =====================================================
    # STORE
    # =====================================================

    path(
        "",
        include("store.urls")
    ),

]