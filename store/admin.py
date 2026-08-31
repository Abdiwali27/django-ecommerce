from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import ContactMessage

from .models import (
    Category,
    Product,
    PaymentSetting,
    Order,
    OrderItem,
)

# =========================================================
# CATEGORY ADMIN
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "created_at",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "-created_at",
    )

# =========================================================
# PRODUCT ADMIN
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "is_available",
        "featured",
        "created_at",
    )

    list_filter = (
        "category",
        "is_available",
        "featured",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "price",
        "stock",
        "is_available",
        "featured",
    )

    ordering = (
        "-created_at",
    )

# =========================================================
# PAYMENT SETTINGS ADMIN
# =========================================================

@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):

    list_display = (
        "zaad_number",
        "edahab_number",
        "sahal_number",
        "updated_at",
    )

    fieldsets = (
        (
            "Mobile Money Payment Numbers",
            {
                "fields": (
                    "zaad_number",
                    "edahab_number",
                    "sahal_number",
                )
            },
        ),
    )

    # Only ONE PaymentSetting can exist
    def has_add_permission(self, request):

        return not PaymentSetting.objects.exists()

    # Do not allow deletion
    def has_delete_permission(
        self,
        request,
        obj=None
    ):

        return False

# =========================================================
# ORDER ADMIN
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "phone",
        "payment_method",
        "mobile_money_provider",
        "total_amount",
        "payment_status",
        "order_status",
        "created_at",
        "order_actions",
    )

    list_filter = (
        "payment_method",
        "mobile_money_provider",
        "payment_status",
        "order_status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    # =====================================================
    # EDIT PAYMENT + ORDER STATUS DIRECTLY FROM TABLE
    # =====================================================

    list_editable = (
        "payment_status",
        "order_status",
    )

    # =====================================================
    # ORDER DETAILS
    # =====================================================

    fieldsets = (

        (
            "Customer Information",
            {
                "fields": (
                    "user",
                    "full_name",
                    "email",
                    "phone",
                    "address",
                    "city",
                    "country",
                )
            },
        ),

        (
            "Order Information",
            {
                "fields": (
                    "total_amount",
                    "order_status",
                )
            },
        ),

        (
            "Payment Information",
            {
                "fields": (
                    "payment_method",
                    "mobile_money_provider",
                    "mobile_money_number",
                    "payment_status",
                )
            },
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )

    # =====================================================
    # ORDER ACTION BUTTONS
    # =====================================================

    @admin.display(description="Actions")
    def order_actions(self, obj):

        # VIEW
        view_url = reverse(
            "order_success",
            kwargs={
                "order_id": obj.id
            }
        )

        # EDIT
        edit_url = reverse(
            "admin:store_order_change",
            args=[obj.id]
        )

        # DELETE
        delete_url = reverse(
            "admin:store_order_delete",
            args=[obj.id]
        )

        return format_html(
            '''
            <div style="
                display: flex;
                gap: 6px;
                align-items: center;
                white-space: nowrap;
            ">

                <!-- VIEW -->

                <a href="{}"
                   style="
                       background: #198754;
                       color: white;
                       padding: 5px 9px;
                       border-radius: 5px;
                       text-decoration: none;
                       font-size: 12px;
                   ">
                    View
                </a>

                <!-- EDIT -->

                <a href="{}"
                   style="
                       background: #0d6efd;
                       color: white;
                       padding: 5px 9px;
                       border-radius: 5px;
                       text-decoration: none;
                       font-size: 12px;
                   ">
                    Edit
                </a>

                <!-- DELETE -->

                <a href="{}"
                   style="
                       background: #dc3545;
                       color: white;
                       padding: 5px 9px;
                       border-radius: 5px;
                       text-decoration: none;
                       font-size: 12px;
                   ">
                    Delete
                </a>

            </div>
            ''',
            view_url,
            edit_url,
            delete_url,
        )

# =========================================================
# ORDER ITEM ADMIN
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product_name",
        "price",
        "quantity",
        "subtotal",
    )

    search_fields = (
        "product_name",
    )

    list_filter = (
        "order",
    )

    ordering = (
        "-order__created_at",
    )



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "subject",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
    )

    readonly_fields = (
        "created_at",
        "replied_at",
    )



