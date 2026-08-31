from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from django.contrib.auth.models import User


# =========================================================
# CATEGORY
# =========================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.name)

            if not base_slug:
                base_slug = "category"

            slug = base_slug
            counter = 1

            while Category.objects.filter(
                slug=slug
            ).exclude(
                pk=self.pk
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):

        return reverse(
            "category_detail",
            kwargs={
                "slug": self.slug
            }
        )


# =========================================================
# PRODUCT
# =========================================================

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_available = models.BooleanField(
        default=True
    )

    featured = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.name)

            if not base_slug:
                base_slug = "product"

            slug = base_slug
            counter = 1

            while Product.objects.filter(
                slug=slug
            ).exclude(
                pk=self.pk
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def current_price(self):

        if self.discount_price:
            return self.discount_price

        return self.price


# =========================================================
# PAYMENT SETTINGS
# =========================================================
#
# ADMIN-KU HALKAN AYUU GELINAYAA BUSINESS NUMBERS:
#
# Zaad     -> zaad_number
# E-Dahab  -> edahab_number
# Sahal    -> sahal_number
#
# Customer-ku numberkan ma gelinayo.
#
# Checkout-ka marka customer-ku doorto provider:
#
# Zaad     -> PaymentSetting.zaad_number
# E-Dahab  -> PaymentSetting.edahab_number
# Sahal    -> PaymentSetting.sahal_number
#
# =========================================================

class PaymentSetting(models.Model):

    zaad_number = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Zaad Business Number",
        help_text="Numberka ganacsiga ee lacagta Zaad lagu soo dirayo."
    )

    edahab_number = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="E-Dahab Business Number",
        help_text="Numberka ganacsiga ee lacagta E-Dahab lagu soo dirayo."
    )

    sahal_number = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Sahal Business Number",
        help_text="Numberka ganacsiga ee lacagta Sahal lagu soo dirayo."
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Payment Setting"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return "Payment Settings"


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):

    # -----------------------------------------------------
    # PAYMENT METHOD
    # -----------------------------------------------------

    PAYMENT_METHOD_CHOICES = [
        ("card", "Card Payment"),
        ("mobile_money", "Mobile Money"),
    ]

    # -----------------------------------------------------
    # MOBILE MONEY PROVIDERS
    # -----------------------------------------------------

    MOBILE_MONEY_CHOICES = [
        ("zaad", "Zaad"),
        ("edahab", "E-Dahab"),
        ("sahal", "Sahal"),
    ]

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    # -----------------------------------------------------
    # ORDER STATUS
    # -----------------------------------------------------

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    # -----------------------------------------------------
    # CUSTOMER INFORMATION
    # -----------------------------------------------------

    full_name = models.CharField(
        max_length=150
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=30
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    country = models.CharField(
        max_length=100,
        default="Somalia"
    )

    # -----------------------------------------------------
    # ORDER TOTAL
    # -----------------------------------------------------

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # -----------------------------------------------------
    # PAYMENT METHOD
    # -----------------------------------------------------

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="mobile_money"
    )

    # -----------------------------------------------------
    # MOBILE MONEY PROVIDER
    # -----------------------------------------------------

    mobile_money_provider = models.CharField(
        max_length=20,
        choices=MOBILE_MONEY_CHOICES,
        blank=True,
        default=""
    )

    # -----------------------------------------------------
    # MOBILE MONEY NUMBER
    # -----------------------------------------------------
    #
    # Field-kan waan ilaalinaynaa si migration/database
    # hore iyo code hore aysan u jabin.
    #
    # IMPORTANT:
    # Tani ma aha business number-ka PaymentSetting.
    #
    # Checkout-ka hadda customer-ka lagama rabo inuu
    # numberkan geliyo.
    #
    # Business numbers waxaa lagu kaydinayaa:
    # PaymentSetting
    #
    # -----------------------------------------------------

    mobile_money_number = models.CharField(
        max_length=30,
        blank=True,
        default=""
    )

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    # -----------------------------------------------------
    # ORDER STATUS
    # -----------------------------------------------------

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="pending"
    )

    # -----------------------------------------------------
    # DATES
    # -----------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"Order #{self.id} - "
            f"{self.full_name}"
        )


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # -----------------------------------------------------
    # PRODUCT SNAPSHOT
    # -----------------------------------------------------

    product_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):

        return (
            f"{self.product_name} "
            f"x {self.quantity}"
        )

class ContactMessage(models.Model):

    STATUS_CHOICES = (
        ("new", "New"),
        ("read", "Read"),
        ("replied", "Replied"),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )

    reply = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    replied_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ["-created_at"]

# =========================================================
# STORE SETTINGS
# =========================================================

class StoreSettings(models.Model):

    store_name = models.CharField(
        max_length=100,
        default="My Store"
    )

    store_email = models.EmailField(
        default="info@mystore.com"
    )

    phone = models.CharField(
        max_length=30,
        default="+252 61 000 0000"
    )

    address = models.CharField(
        max_length=255,
        default="Mogadishu, Somalia"
    )

    opening_time = models.TimeField(
        default="08:00"
    )

    closing_time = models.TimeField(
        default="20:00"
    )

    currency = models.CharField(
        max_length=10,
        default="USD"
    )

    shipping_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    free_shipping_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return self.store_name

    class Meta:

        verbose_name = "Store Settings"

        verbose_name_plural = "Store Settings"
