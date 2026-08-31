from django.urls import path

from . import views


urlpatterns = [
    path(
    "",
    views.home,
    name="home"
   ),

   # About
   path("about/", views.about, name="about"),
   path("contact/", views.contact, name="contact"),

   path(
    "messages/",
    views.customer_messages,
    name="customer_messages"
),

path(
    "messages/<int:pk>/",
    views.customer_message_detail,
    name="customer_message_detail"
),
path(
    "messages/<int:pk>/delete/",
    views.customer_message_delete,
    name="customer_message_delete"
),
    # =====================================================
    # PRODUCTS
    # =====================================================

     path(
    "shop/",
    views.product_list,
    name="product_list"
    ),

    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),
    # =========================================================
# PRODUCT MANAGEMENT
# =========================================================

path(
    "products/manage/",
    views.product_management,
    name="product_management"
),

path(
    "products/add/",
    views.product_create,
    name="product_create"
),

path(
    "products/<int:pk>/edit/",
    views.product_update,
    name="product_update"
),

path(
    "products/<int:pk>/delete/",
    views.product_delete,
    name="product_delete"
),


    # =====================================================
    # CART
    # =====================================================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.cart_add,
        name="cart_add"
    ),

    path(
        "cart/increase/<int:product_id>/",
        views.cart_increase,
        name="cart_increase"
    ),

    path(
        "cart/decrease/<int:product_id>/",
        views.cart_decrease,
        name="cart_decrease"
    ),

    path(
        "cart/remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove"
    ),

    path(
        "cart/clear/",
        views.cart_clear,
        name="cart_clear"
    ),


    # =====================================================
    # CHECKOUT
    # =====================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "order/success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),


    # =====================================================
    # ORDER MANAGEMENT
    # =====================================================

    path(
        "orders/",
        views.order_list,
        name="order_list"
    ),

    path(
        "orders/<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),

    path(
        "orders/<int:order_id>/update/",
        views.order_update,
        name="order_update"
    ),

    path(
        "orders/<int:order_id>/delete/",
        views.order_delete,
        name="order_delete"
    ),
     # =====================================================
    # DASHBOARD
    # =====================================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),
 
    path(
    "products/manage/",
    views.product_management,
    name="product_management"
),
 
 # =====================================================
# CATEGORY MANAGEMENT
# =====================================================

path(
    "categories/manage/",
    views.category_management,
    name="category_management"
),

path(
    "categories/add/",
    views.category_create,
    name="category_create"
),

path(
    "categories/<int:pk>/edit/",
    views.category_update,
    name="category_update"
),

path(
    "categories/<slug:slug>/",
    views.category_detail,
    name="category_detail"
),

path(
    "categories/<int:pk>/delete/",
    views.category_delete,
    name="category_delete"
),
# =====================================================
    # PAYMENT SETTINGS
    # =====================================================

    path(
        "payment-settings/",
        views.payment_settings,
        name="payment_settings"
    ),

    path(
        "payment-settings/edit/",
        views.payment_settings_update,
        name="payment_settings_update"
    ),
# =====================================================
# REPORTS
# =====================================================

path(
    "reports/",
    views.reports,
    name="reports"
),
# =====================================================
# USER MANAGEMENT
# =====================================================

path(
    "users/",
    views.user_management,
    name="user_management"
),

# =====================================================
# USER MANAGEMENT
# =====================================================

path(
    "users/",
    views.user_management,
    name="user_management"
),

path(
    "users/add/",
    views.user_create,
    name="user_create"
),

path(
    "users/<int:pk>/edit/",
    views.user_edit,
    name="user_edit"
),

path(
    "users/<int:pk>/delete/",
    views.user_confirm_delete,
    name="user_confirm_delete"
),
# =====================================================
# STORE SETTINGS
# =====================================================

path(
    "settings/",
    views.store_settings_view,
    name="store_settings"
),

    


]