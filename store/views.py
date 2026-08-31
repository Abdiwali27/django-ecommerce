import json
from decimal import Decimal
from datetime import timedelta
from .models import StoreSettings
from django.contrib import messages
from django.db import transaction
from django.db.models import (
    Sum,
    Count,
    Q,
    F,
    ExpressionWrapper,
    DecimalField,
)
from django.db.models.functions import ExtractMonth

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.utils import timezone

from .forms import (
    CheckoutForm,
    OrderUpdateForm,
    CategoryForm,
    ProductForm,
)

from .models import (
    Product,
    Category,
    PaymentSetting,
    Order,
    OrderItem,
)
from .models import ContactMessage
 
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
 
 

# =========================================================
# PRODUCT LIST
# =========================================================

def product_list(request):

    products = Product.objects.filter(
        is_available=True
    ).select_related(
        "category"
    )

    categories = Category.objects.all()

    category_slug = request.GET.get(
        "category",
        ""
    ).strip()

    if category_slug:

        products = products.filter(
            category__slug=category_slug
        )

    context = {

        "products": products,

        "categories": categories,

        "selected_category": category_slug,

    }

    return render(
        request,
        "store/product_list.html",
        context
    )


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects.select_related(
            "category"
        ),
        slug=slug,
        is_available=True
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product
        }
    )


# =========================================================
# CART
# =========================================================

def cart(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    cart_items = []

    cart_total = Decimal("0.00")

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id,
                is_available=True
            )

        except Product.DoesNotExist:

            continue

        try:

            quantity = int(quantity)

        except (ValueError, TypeError):

            continue

        if quantity <= 0:
            continue

        subtotal = (
            product.current_price * quantity
        )

        cart_total += subtotal

        cart_items.append({

            "product": product,

            "quantity": quantity,

            "subtotal": subtotal,

        })

    context = {

        "cart_items": cart_items,

        "cart_total": cart_total,

    }

    return render(
        request,
        "store/cart.html",
        context
    )


# =========================================================
# ADD TO CART
# =========================================================

def cart_add(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product.id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# INCREASE QUANTITY
# =========================================================

def cart_increase(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# DECREASE QUANTITY
# =========================================================

def cart_decrease(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:

            del cart[product_id]

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# REMOVE FROM CART
# =========================================================

def cart_remove(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        del cart[product_id]

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# CLEAR CART
# =========================================================

def cart_clear(request):

    request.session["cart"] = {}

    request.session.modified = True

    return redirect("cart")


# =========================================================
# CHECKOUT
# =========================================================

def checkout(request):

    payment_settings = (
        PaymentSetting.objects.first()
    )

    if payment_settings is None:

        payment_settings = (
            PaymentSetting.objects.create()
        )

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    cart_items = []

    cart_total = Decimal("0.00")

    valid_cart = {}

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id,
                is_available=True
            )

        except Product.DoesNotExist:

            continue

        try:

            quantity = int(quantity)

        except (ValueError, TypeError):

            continue

        if quantity <= 0:
            continue

        subtotal = (
            product.current_price * quantity
        )

        cart_total += subtotal

        valid_cart[str(product.id)] = quantity

        cart_items.append({

            "product": product,

            "quantity": quantity,

            "subtotal": subtotal,

        })

    if not cart_items:

        request.session["cart"] = {}

        request.session.modified = True

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    request.session["cart"] = valid_cart

    request.session.modified = True

    if request.method == "POST":

        form = CheckoutForm(
            request.POST
        )

        if form.is_valid():

            return create_order(
                request,
                form
            )

    else:

        form = CheckoutForm()

    context = {

        "form": form,

        "payment_settings":
            payment_settings,

        "cart_items":
            cart_items,

        "cart_total":
            cart_total,

    }

    return render(
        request,
        "store/checkout.html",
        context
    )


# =========================================================
# CREATE ORDER
# =========================================================

def create_order(request, form):

    full_name = form.cleaned_data.get(
        "full_name"
    )

    email = form.cleaned_data.get(
        "email"
    )

    phone = form.cleaned_data.get(
        "phone"
    )

    address = form.cleaned_data.get(
        "address"
    )

    city = form.cleaned_data.get(
        "city"
    )

    payment_method = form.cleaned_data.get(
        "payment_method"
    )

    mobile_money_provider = (
        form.cleaned_data.get(
            "mobile_money_provider"
        )
    )

    if payment_method not in [
        "card",
        "mobile_money",
    ]:

        messages.error(
            request,
            "Please select a payment method."
        )

        return redirect("checkout")

    if payment_method == "mobile_money":

        if mobile_money_provider not in [
            "zaad",
            "edahab",
            "sahal",
        ]:

            messages.error(
                request,
                "Please select Zaad, E-Dahab or Sahal."
            )

            return redirect("checkout")

    else:

        mobile_money_provider = ""

    cart = request.session.get(
        "cart",
        {}
    )

    if not cart:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    try:

        with transaction.atomic():

            total_amount = Decimal("0.00")

            cart_items = []

            for product_id, quantity in cart.items():

                product = Product.objects.get(
                    id=product_id,
                    is_available=True
                )

                quantity = int(quantity)

                if quantity <= 0:
                    continue

                subtotal = (
                    product.current_price
                    * quantity
                )

                total_amount += subtotal

                cart_items.append({

                    "product": product,

                    "quantity": quantity,

                    "subtotal": subtotal,

                })

            if not cart_items:

                raise Product.DoesNotExist

            order = Order.objects.create(

                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),

                full_name=full_name,

                email=email,

                phone=phone,

                address=address,

                city=city,

                payment_method=payment_method,

                mobile_money_provider=
                    mobile_money_provider,

                total_amount=total_amount,

                payment_status="pending",

                order_status="pending",

            )

            for item in cart_items:

                product = item["product"]

                OrderItem.objects.create(

                    order=order,

                    product=product,

                    product_name=product.name,

                    price=product.current_price,

                    quantity=item["quantity"],

                    subtotal=item["subtotal"],

                )

            request.session["cart"] = {}

            request.session.modified = True

        messages.success(
            request,
            f"Order #{order.id} has been placed successfully!"
        )

        return redirect(
            "order_success",
            order_id=order.id
        )

    except Product.DoesNotExist:

        messages.error(
            request,
            "One of the products in your cart is no longer available."
        )

        return redirect("cart")

    except Exception as e:

        print(
            "CREATE ORDER ERROR:",
            e
        )

        messages.error(
            request,
            "Something went wrong while creating your order."
        )

        return redirect("checkout")


# =========================================================
# ORDER SUCCESS
# =========================================================

def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    return render(
        request,
        "store/order_success.html",
        {
            "order": order
        }
    )


# =========================================================
# ORDER MANAGEMENT
# =========================================================
@login_required
def order_list(request):

    orders = Order.objects.all().order_by(
        "-created_at"
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        orders = orders.filter(
            Q(full_name__icontains=search)
            |
            Q(email__icontains=search)
            |
            Q(phone__icontains=search)
        )

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    payment_status = request.GET.get(
        "payment_status",
        ""
    )

    if payment_status:

        orders = orders.filter(
            payment_status=payment_status
        )

    # -----------------------------------------------------
    # ORDER STATUS
    # -----------------------------------------------------

    order_status = request.GET.get(
        "order_status",
        ""
    )

    if order_status:

        orders = orders.filter(
            order_status=order_status
        )

    context = {

        "orders": orders,

        "search": search,

        "selected_payment_status":
            payment_status,

        "selected_order_status":
            order_status,

        "payment_status_choices":
            Order.PAYMENT_STATUS_CHOICES,

        "order_status_choices":
            Order.ORDER_STATUS_CHOICES,

    }

    return render(
        request,
        "store/order_list.html",
        context
    )


# =========================================================
# ORDER DETAIL
# =========================================================

def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items"
        ),
        id=order_id
    )

    context = {

        "order": order,

        "items": order.items.all(),

    }

    return render(
        request,
        "store/order_detail.html",
        context
    )


# =========================================================
# ORDER UPDATE
# =========================================================

def order_update(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == "POST":

        form = OrderUpdateForm(
            request.POST,
            instance=order
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f"Order #{order.id} has been updated successfully."
            )

            return redirect(
                "order_detail",
                order_id=order.id
            )

    else:

        form = OrderUpdateForm(
            instance=order
        )

    return render(
        request,
        "store/order_update.html",
        {
            "order": order,
            "form": form,
        }
    )


# =========================================================
# ORDER DELETE
# =========================================================

def order_delete(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == "POST":

        order_number = order.id

        order.delete()

        messages.success(
            request,
            f"Order #{order_number} has been deleted."
        )

        return redirect(
            "order_list"
        )

    return render(
        request,
        "store/order_detail.html",
        {
            "order": order
        }
    )


# =========================================================
# DASHBOARD
# =========================================================
@login_required
def dashboard(request):

    # =====================================================
    # BASIC STATISTICS
    # =====================================================

    total_products = Product.objects.count()

    total_categories = Category.objects.count()

    total_orders = Order.objects.count()

    # =====================================================
    # ORDER STATUS
    # =====================================================

    pending_orders = Order.objects.filter(
        order_status="pending"
    ).count()

    confirmed_orders = Order.objects.filter(
        order_status="confirmed"
    ).count()

    processing_orders = Order.objects.filter(
        order_status="processing"
    ).count()

    shipped_orders = Order.objects.filter(
        order_status="shipped"
    ).count()

    delivered_orders = Order.objects.filter(
        order_status="delivered"
    ).count()

    cancelled_orders = Order.objects.filter(
        order_status="cancelled"
    ).count()

    # =====================================================
    # PAYMENT STATUS
    # =====================================================

    pending_payments = Order.objects.filter(
        payment_status="pending"
    ).count()

    paid_orders = Order.objects.filter(
        payment_status="paid"
    ).count()

    failed_payments = Order.objects.filter(
        payment_status="failed"
    ).count()

    # =====================================================
    # TOTAL SALES
    # =====================================================
    # Sales = all orders except cancelled orders.
    # Pending orders are still counted as sales/orders placed.
    # =====================================================

    total_sales = (
        Order.objects
        .exclude(
            order_status="cancelled"
        )
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # REVENUE
    # =====================================================
    # Revenue = only money from paid orders.
    # =====================================================

    revenue = (
        Order.objects
        .filter(
            payment_status="paid"
        )
        .exclude(
            order_status="cancelled"
        )
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # LOW STOCK
    # =====================================================

    low_stock_products = Product.objects.filter(
        stock__lte=5,
        is_available=True
    ).count()

    # =====================================================
    # RECENT ORDERS
    # =====================================================

    recent_orders = (
        Order.objects
        .select_related("user")
        .order_by("-created_at")[:5]
    )

    # =====================================================
    # RECENT PRODUCTS
    # =====================================================

    recent_products = (
        Product.objects
        .select_related("category")
        .order_by("-created_at")[:5]
    )

    # =====================================================
    # ORDERS BY MONTH
    # =====================================================
    #
    # Current year only.
    #
    # Example:
    # Jan -> 5
    # Feb -> 10
    # Mar -> 7
    #
    # =====================================================

    current_year = timezone.localdate().year

    monthly_orders = (
        Order.objects
        .filter(
            created_at__year=current_year
        )
        .annotate(
            month=ExtractMonth("created_at")
        )
        .values("month")
        .annotate(
            orders=Count("id")
        )
        .order_by("month")
    )

    monthly_orders_dict = {
        item["month"]: item["orders"]
        for item in monthly_orders
    }

    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    orders_by_month = []

    for month_number, month_name in enumerate(
        month_names,
        start=1
    ):

        orders_by_month.append({

            "month": month_name,

            "orders":
                monthly_orders_dict.get(
                    month_number,
                    0
                ),

        })

    # =====================================================
    # SALES / REVENUE BY MONTH
    # =====================================================

    monthly_sales = (
        Order.objects
        .filter(
            created_at__year=current_year
        )
        .exclude(
            order_status="cancelled"
        )
        .annotate(
            month=ExtractMonth("created_at")
        )
        .values("month")
        .annotate(
            sales=Sum("total_amount")
        )
        .order_by("month")
    )

    monthly_revenue = (
        Order.objects
        .filter(
            created_at__year=current_year,
            payment_status="paid"
        )
        .exclude(
            order_status="cancelled"
        )
        .annotate(
            month=ExtractMonth("created_at")
        )
        .values("month")
        .annotate(
            revenue=Sum("total_amount")
        )
        .order_by("month")
    )

    sales_dict = {
        item["month"]: float(
            item["sales"] or 0
        )
        for item in monthly_sales
    }

    revenue_dict = {
        item["month"]: float(
            item["revenue"] or 0
        )
        for item in monthly_revenue
    }

    sales_revenue_by_month = []

    for month_number, month_name in enumerate(
        month_names,
        start=1
    ):

        sales_revenue_by_month.append({

            "month": month_name,

            "sales":
                sales_dict.get(
                    month_number,
                    0
                ),

            "revenue":
                revenue_dict.get(
                    month_number,
                    0
                ),

        })

    # =====================================================
    # JSON DATA FOR CHARTS
    # =====================================================

    orders_by_month_json = json.dumps(
        orders_by_month
    )

    sales_revenue_by_month_json = json.dumps(
        sales_revenue_by_month
    )

    # =====================================================
    # DASHBOARD CONTEXT
    # =====================================================

    context = {

        # Basic statistics
        "total_products":
            total_products,

        "total_categories":
            total_categories,

        "total_orders":
            total_orders,

        # Order status
        "pending_orders":
            pending_orders,

        "confirmed_orders":
            confirmed_orders,

        "processing_orders":
            processing_orders,

        "shipped_orders":
            shipped_orders,

        "delivered_orders":
            delivered_orders,

        "cancelled_orders":
            cancelled_orders,

        # Payment status
        "pending_payments":
            pending_payments,

        "paid_orders":
            paid_orders,

        "failed_payments":
            failed_payments,

        # Financial
        "total_sales":
            total_sales,

        "revenue":
            revenue,

        # Stock
        "low_stock_products":
            low_stock_products,

        # Recent data
        "recent_orders":
            recent_orders,

        "recent_products":
            recent_products,

        # Orders by month
        "orders_by_month":
            orders_by_month,

        "orders_by_month_json":
            orders_by_month_json,

        # Sales / Revenue chart
        "sales_revenue_by_month":
            sales_revenue_by_month,

        "sales_revenue_by_month_json":
            sales_revenue_by_month_json,

        # Year
        "current_year":
            current_year,

    }

    return render(
        request,
        "store/dashboard.html",
        context
    )


# =========================================================
# PRODUCT MANAGEMENT
# =========================================================
@login_required
def product_management(request):

    products = (
        Product.objects
        .select_related("category")
        .all()
        .order_by("-created_at")
    )

    categories = Category.objects.all()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        products = products.filter(

            Q(name__icontains=search)

            |

            Q(description__icontains=search)

            |

            Q(
                category__name__icontains=search
            )

        )

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    category_id = request.GET.get(
        "category",
        ""
    )

    if category_id:

        products = products.filter(
            category_id=category_id
        )

    # -----------------------------------------------------
    # STOCK FILTER
    # -----------------------------------------------------

    stock_status = request.GET.get(
        "stock",
        ""
    )

    if stock_status == "in_stock":

        products = products.filter(
            stock__gt=0
        )

    elif stock_status == "out_of_stock":

        products = products.filter(
            stock=0
        )

    elif stock_status == "low_stock":

        products = products.filter(
            stock__lte=5
        )

    # -----------------------------------------------------
    # AVAILABILITY FILTER
    # -----------------------------------------------------

    availability = request.GET.get(
        "availability",
        ""
    )

    if availability == "available":

        products = products.filter(
            is_available=True
        )

    elif availability == "unavailable":

        products = products.filter(
            is_available=False
        )

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "products":
            products,

        "categories":
            categories,

        "search":
            search,

        "selected_category":
            category_id,

        "selected_stock":
            stock_status,

        "selected_availability":
            availability,

    }

    return render(
        request,
        "store/product_management.html",
        context
    )


# =========================================================
# PRODUCT CREATE
# =========================================================

def product_create(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                f"Product '{product.name}' added successfully."
            )

            return redirect(
                "product_management"
            )

    else:

        form = ProductForm()

    return render(
        request,
        "store/product_form.html",
        {
            "form": form,
            "page_title": "Add Product",
            "button_text": "Add Product",
        }
    )


# =========================================================
# PRODUCT UPDATE
# =========================================================

def product_update(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                f"Product '{product.name}' updated successfully."
            )

            return redirect(
                "product_management"
            )

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "store/product_form.html",
        {
            "form": form,
            "product": product,
            "page_title": "Edit Product",
            "button_text": "Update Product",
        }
    )


# =========================================================
# PRODUCT DELETE
# =========================================================

def product_delete(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == "POST":

        product_name = product.name

        product.delete()

        messages.success(
            request,
            f"Product '{product_name}' deleted successfully."
        )

        return redirect(
            "product_management"
        )

    return render(
        request,
        "store/product_delete.html",
        {
            "product": product
        }
    )


# =========================================================
# CATEGORY MANAGEMENT
# =========================================================

def category_management(request):

    categories = Category.objects.all().order_by(
        "-id"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        categories = categories.filter(
            name__icontains=search
        )

    context = {

        "categories":
            categories,

        "search":
            search,

    }

    return render(
        request,
        "store/category_management.html",
        context
    )


# =========================================================
# CATEGORY CREATE
# =========================================================

def category_create(request):

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category has been created successfully."
            )

            return redirect(
                "category_management"
            )

    else:

        form = CategoryForm()

    return render(
        request,
        "store/category_form.html",
        {
            "form": form,
            "title": "Add Category",
        }
    )


# =========================================================
# CATEGORY UPDATE
# =========================================================

def category_update(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES,
            instance=category
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category has been updated successfully."
            )

            return redirect(
                "category_management"
            )

    else:

        form = CategoryForm(
            instance=category
        )

    return render(
        request,
        "store/category_form.html",
        {
            "form": form,
            "title": "Edit Category",
            "category": category,
        }
    )


# =========================================================
# CATEGORY DELETE
# =========================================================

def category_delete(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":

        category_name = category.name

        category.delete()

        messages.success(
            request,
            f"Category '{category_name}' has been deleted successfully."
        )

        return redirect(
            "category_management"
        )

    return render(
        request,
        "store/category_delete.html",
        {
            "category": category,
        }
    )


# =========================================================
# CATEGORY DETAIL
# =========================================================

def category_detail(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    products = (
        Product.objects
        .filter(
            category=category,
            is_available=True
        )
        .select_related("category")
    )

    return render(
        request,
        "store/category_detail.html",
        {
            "category": category,
            "products": products,
        }
    )


# =========================================================
# PAYMENT SETTINGS
# =========================================================

def payment_settings(request):

    settings = PaymentSetting.objects.first()

    if settings is None:

        settings = PaymentSetting.objects.create()

    return render(
        request,
        "store/payment_settings.html",
        {
            "settings": settings,
        }
    )


# =========================================================
# PAYMENT SETTINGS UPDATE
# =========================================================

def payment_settings_update(request):

    settings = PaymentSetting.objects.first()

    if settings is None:

        settings = PaymentSetting.objects.create()

    if request.method == "POST":

        settings.zaad_number = request.POST.get(
            "zaad_number",
            ""
        ).strip()

        settings.edahab_number = request.POST.get(
            "edahab_number",
            ""
        ).strip()

        settings.sahal_number = request.POST.get(
            "sahal_number",
            ""
        ).strip()

        settings.save()

        messages.success(
            request,
            "Payment settings updated successfully."
        )

        return redirect(
            "payment_settings"
        )

    return render(
        request,
        "store/payment_settings_update.html",
        {
            "settings": settings,
        }
    )


# =========================================================
# REPORTS MANAGEMENT
# =========================================================

def reports(request):

    # =====================================================
    # DATE FILTER
    # =====================================================

    today = timezone.localdate()

    start_date = request.GET.get(
        "start_date",
        ""
    ).strip()

    end_date = request.GET.get(
        "end_date",
        ""
    ).strip()

    orders = Order.objects.all()

    # -----------------------------------------------------
    # START DATE
    # -----------------------------------------------------

    if start_date:

        orders = orders.filter(
            created_at__date__gte=start_date
        )

    # -----------------------------------------------------
    # END DATE
    # -----------------------------------------------------

    if end_date:

        orders = orders.filter(
            created_at__date__lte=end_date
        )

    # =====================================================
    # BASIC STATISTICS
    # =====================================================

    total_orders = orders.count()

    pending_orders = orders.filter(
        order_status="pending"
    ).count()

    paid_orders = orders.filter(
        payment_status="paid"
    ).count()

    failed_payments = orders.filter(
        payment_status="failed"
    ).count()

    cancelled_orders = orders.filter(
        order_status="cancelled"
    ).count()

    processing_orders = orders.filter(
        order_status="processing"
    ).count()

    shipped_orders = orders.filter(
        order_status="shipped"
    ).count()

    delivered_orders = orders.filter(
        order_status="delivered"
    ).count()

    confirmed_orders = orders.filter(
        order_status="confirmed"
    ).count()

    # =====================================================
    # TOTAL SALES
    # =====================================================

    total_sales = (
        orders
        .exclude(
            order_status="cancelled"
        )
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # REVENUE
    # =====================================================

    revenue = (
        orders
        .filter(
            payment_status="paid"
        )
        .exclude(
            order_status="cancelled"
        )
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # OUTSTANDING
    # =====================================================

    outstanding = (
        orders
        .filter(
            payment_status="pending"
        )
        .exclude(
            order_status="cancelled"
        )
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    # =====================================================
    # RECENT ORDERS
    # =====================================================

    recent_orders = (
        orders
        .select_related("user")
        .order_by("-created_at")[:10]
    )

    # =====================================================
    # PRODUCT SALES
    # =====================================================

    product_sales = (
        OrderItem.objects
        .filter(
            order__in=orders,
            order__payment_status="paid"
        )
        .values(
            "product_name"
        )
        .annotate(

            total_quantity=Sum(
                "quantity"
            ),

            total_sales=Sum(
                ExpressionWrapper(
                    F("price") * F("quantity"),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2
                    )
                )
            ),

        )
        .order_by(
            "-total_sales"
        )[:10]
    )

    # =====================================================
    # PAYMENT STATUS REPORT
    # =====================================================

    payment_status_report = (
        orders
        .values(
            "payment_status"
        )
        .annotate(

            count=Count("id"),

            amount=Sum(
                "total_amount"
            ),

        )
        .order_by(
            "payment_status"
        )
    )

    # =====================================================
    # ORDER STATUS REPORT
    # =====================================================

    order_status_report = (
        orders
        .values(
            "order_status"
        )
        .annotate(

            count=Count("id"),

            amount=Sum(
                "total_amount"
            ),

        )
        .order_by(
            "order_status"
        )
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "total_orders":
            total_orders,

        "pending_orders":
            pending_orders,

        "confirmed_orders":
            confirmed_orders,

        "processing_orders":
            processing_orders,

        "shipped_orders":
            shipped_orders,

        "delivered_orders":
            delivered_orders,

        "cancelled_orders":
            cancelled_orders,

        "paid_orders":
            paid_orders,

        "failed_payments":
            failed_payments,

        "total_sales":
            total_sales,

        "revenue":
            revenue,

        "outstanding":
            outstanding,

        "recent_orders":
            recent_orders,

        "product_sales":
            product_sales,

        "payment_status_report":
            payment_status_report,

        "order_status_report":
            order_status_report,

        "start_date":
            start_date,

        "end_date":
            end_date,

        "today":
            today,

    }

    return render(
        request,
        "store/reports.html",
        context
    )

# =========================================================
# HOME PAGE
# =========================================================

def home(request):

    featured_products = Product.objects.filter(
        is_available=True
    ).select_related(
        "category"
    ).order_by(
        "-created_at"
    )[:8]

    categories = Category.objects.all().order_by(
        "name"
    )[:6]

    total_products = Product.objects.filter(
        is_available=True
    ).count()

    context = {
        "featured_products": featured_products,
        "categories": categories,
        "total_products": total_products,
    }

    return render(
        request,
        "store/home.html",
        context
    )



def about(request):
    return render(
        request,
        "store/about.html"
    )

def contact(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            status="new",
        )

        messages.success(
            request,
            "Your message has been sent successfully. We will get back to you soon."
        )

        return redirect("contact")

    return render(
        request,
        "store/contact.html"
    )
@login_required
def customer_messages(request):

    contact_messages = ContactMessage.objects.all()

    unread_messages_count = ContactMessage.objects.filter(
        status="new"
    ).count()

    return render(
        request,
        "store/customer_messages.html",
        {
            "contact_messages": contact_messages,
            "unread_messages_count": unread_messages_count,
        }
    )

def customer_message_detail(request, pk):

    contact_message = get_object_or_404(
        ContactMessage,
        pk=pk
    )

    # Mark as read
    if contact_message.status == "new":

        contact_message.status = "read"

        contact_message.save(
            update_fields=["status"]
        )

    if request.method == "POST":

        reply = request.POST.get(
            "reply",
            ""
        ).strip()

        if reply:

            send_mail(
                subject=f"Re: {contact_message.subject}",

                message=reply,

                from_email=None,

                recipient_list=[
                    contact_message.email
                ],

                fail_silently=False,
            )

            contact_message.reply = reply
            contact_message.status = "replied"
            contact_message.replied_at = timezone.now()

            contact_message.save()

            messages.success(
                request,
                "Reply sent successfully."
            )

            return redirect(
                "customer_message_detail",
                pk=contact_message.pk
            )

    unread_messages_count = ContactMessage.objects.filter(
        status="new"
    ).count()

    return render(
        request,
        "store/customer_message_detail.html",
        {
            "contact_message": contact_message,
            "unread_messages_count": unread_messages_count,
        }
    )

def customer_message_delete(request, pk):

    contact_message = get_object_or_404(
        ContactMessage,
        pk=pk
    )

    if request.method == "POST":

        contact_message.delete()

        messages.success(
            request,
            "Customer message deleted successfully."
        )

        return redirect("customer_messages")

    return render(
        request,
        "store/customer_message_delete.html",
        {
            "contact_message": contact_message
        }
    )



def superuser_required(view_func):

    return user_passes_test(
        lambda user: user.is_authenticated and user.is_superuser
    )(view_func)

@superuser_required
def user_management(request):

    users = User.objects.all().order_by("-date_joined")

    return render(
        request,
        "store/user_management.html",
        {
            "users": users
        }
    )

# =========================================================
# USER MANAGEMENT
# =========================================================

User = get_user_model()


# ---------------------------------------------------------
# ONLY SUPERUSER CAN ACCESS USER MANAGEMENT
# ---------------------------------------------------------

def superuser_required(view_func):

    return user_passes_test(
        lambda user: user.is_authenticated and user.is_superuser
    )(view_func)


# =========================================================
# USER LIST
# =========================================================

@superuser_required
def user_management(request):

    users = User.objects.all().order_by(
        "-date_joined"
    )

    return render(
        request,
        "store/user_management.html",
        {
            "users": users
        }
    )


# =========================================================
# CREATE USER
# =========================================================

@superuser_required
def user_create(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        is_staff = request.POST.get(
            "is_staff"
        ) == "on"

        is_superuser = request.POST.get(
            "is_superuser"
        ) == "on"

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not username:

            messages.error(
                request,
                "Username is required."
            )

            return redirect(
                "user_create"
            )


        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "This username already exists."
            )

            return redirect(
                "user_create"
            )


        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "user_create"
            )


        if not password:

            messages.error(
                request,
                "Password is required."
            )

            return redirect(
                "user_create"
            )


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password,

            is_staff=is_staff,

            is_superuser=is_superuser,

        )


        messages.success(
            request,
            f"User '{username}' has been created successfully."
        )


        return redirect(
            "user_management"
        )


    return render(
        request,
        "store/user_create.html"
    )


# =========================================================
# EDIT USER
# =========================================================

@superuser_required
def user_edit(request, pk):

    user = get_object_or_404(
        User,
        pk=pk
    )


    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        is_staff = request.POST.get(
            "is_staff"
        ) == "on"

        is_superuser = request.POST.get(
            "is_superuser"
        ) == "on"

        # -------------------------------------------------
        # USERNAME VALIDATION
        # -------------------------------------------------

        if not username:

            messages.error(
                request,
                "Username is required."
            )

            return redirect(
                "user_edit",
                pk=user.pk
            )


        username_exists = User.objects.filter(
            username=username
        ).exclude(
            pk=user.pk
        ).exists()


        if username_exists:

            messages.error(
                request,
                "This username already exists."
            )

            return redirect(
                "user_edit",
                pk=user.pk
            )


        # -------------------------------------------------
        # UPDATE USER
        # -------------------------------------------------

        user.username = username

        user.email = email

        user.is_staff = is_staff

        user.is_superuser = is_superuser


        # -------------------------------------------------
        # UPDATE PASSWORD ONLY IF PROVIDED
        # -------------------------------------------------

        if password:

            user.set_password(
                password
            )


        user.save()


        messages.success(
            request,
            f"User '{user.username}' has been updated successfully."
        )


        return redirect(
            "user_management"
        )


    return render(
        request,
        "store/user_edit.html",
        {
            "user": user
        }
    )


# =========================================================
# DELETE USER
# =========================================================

@superuser_required
def user_confirm_delete(request, pk):

    user = get_object_or_404(
        User,
        pk=pk
    )


    # -----------------------------------------------------
    # PREVENT DELETING YOURSELF
    # -----------------------------------------------------

    if user.pk == request.user.pk:

        messages.error(
            request,
            "You cannot delete your own account."
        )

        return redirect(
            "user_management"
        )


    if request.method == "POST":

        username = user.username

        user.delete()


        messages.success(
            request,
            f"User '{username}' has been deleted successfully."
        )


        return redirect(
            "user_management"
        )


    return render(
        request,
        "store/user_confirm_delete.html",
        {
            "user": user
        }
    )
# =========================================================
# STORE SETTINGS
# =========================================================

@superuser_required
def store_settings_view(request):

    settings = StoreSettings.objects.first()

    if not settings:

        settings = StoreSettings.objects.create()


    if request.method == "POST":

        settings.store_name = request.POST.get(
            "store_name",
            ""
        ).strip()

        settings.store_email = request.POST.get(
            "store_email",
            ""
        ).strip()

        settings.phone = request.POST.get(
            "phone",
            ""
        ).strip()

        settings.address = request.POST.get(
            "address",
            ""
        ).strip()

        settings.opening_time = request.POST.get(
            "opening_time"
        )

        settings.closing_time = request.POST.get(
            "closing_time"
        )

        settings.currency = request.POST.get(
            "currency",
            "USD"
        )

        settings.shipping_fee = request.POST.get(
            "shipping_fee",
            0
        )

        settings.free_shipping_minimum = request.POST.get(
            "free_shipping_minimum",
            50
        )

        settings.save()

        messages.success(
            request,
            "Store settings updated successfully."
        )

        return redirect(
            "store_settings"
        )


    return render(
        request,
        "store/store_settings.html",
        {
            "settings": settings
        }
    )