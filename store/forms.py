from django import forms

from .models import Order
 

 

from .models import Category, Product



# =========================================================
# CHECKOUT FORM
# =========================================================

class CheckoutForm(forms.Form):

    # =========================================================
    # CUSTOMER INFORMATION
    # =========================================================

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your full name",
            }
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
            }
        ),
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your phone number",
                "inputmode": "tel",
            }
        ),
    )

    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Your delivery address",
            }
        ),
    )

    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your city",
            }
        ),
    )

    # =========================================================
    # PAYMENT METHOD
    # =========================================================

    payment_method = forms.ChoiceField(
        choices=[
            ("card", "Card Payment"),
            ("mobile_money", "Mobile Money"),
        ],
        widget=forms.RadioSelect(
            attrs={
                "class": "payment-method-radio",
            }
        ),
    )

    # =========================================================
    # MOBILE MONEY PROVIDER
    # =========================================================

    mobile_money_provider = forms.ChoiceField(
        required=False,
        choices=[
            ("zaad", "Zaad"),
            ("edahab", "E-Dahab"),
            ("sahal", "Sahal"),
        ],
        widget=forms.RadioSelect(
            attrs={
                "class": "mobile-provider-radio",
            }
        ),
    )

    # =========================================================
    # CARD DETAILS
    # =========================================================

    card_holder = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Card holder name",
            }
        ),
    )

    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "1234 5678 9012 3456",
                "inputmode": "numeric",
            }
        ),
    )

    expiry_date = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "MM/YY",
            }
        ),
    )

    cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "CVV",
            }
        ),
    )

    # =========================================================
    # VALIDATION
    # =========================================================

    def clean(self):

        cleaned_data = super().clean()

        payment_method = cleaned_data.get(
            "payment_method"
        )

        mobile_money_provider = cleaned_data.get(
            "mobile_money_provider"
        )

        card_holder = cleaned_data.get(
            "card_holder"
        )

        card_number = cleaned_data.get(
            "card_number"
        )

        expiry_date = cleaned_data.get(
            "expiry_date"
        )

        cvv = cleaned_data.get(
            "cvv"
        )

        # =====================================================
        # MOBILE MONEY
        # =====================================================

        if payment_method == "mobile_money":

            if not mobile_money_provider:

                self.add_error(
                    "mobile_money_provider",
                    "Please select Zaad, E-Dahab or Sahal.",
                )

        # =====================================================
        # CARD
        # =====================================================

        if payment_method == "card":

            if not card_holder:

                self.add_error(
                    "card_holder",
                    "Card holder name is required.",
                )

            if not card_number:

                self.add_error(
                    "card_number",
                    "Card number is required.",
                )

            if not expiry_date:

                self.add_error(
                    "expiry_date",
                    "Expiry date is required.",
                )

            if not cvv:

                self.add_error(
                    "cvv",
                    "CVV is required.",
                )

        return cleaned_data


# =========================================================
# ORDER UPDATE FORM
# =========================================================

class OrderUpdateForm(forms.ModelForm):

    class Meta:

        model = Order

        fields = [
            "payment_status",
            "order_status",
        ]

        widgets = {

            "payment_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "order_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

        labels = {

            "payment_status":
                "Payment Status",

            "order_status":
                "Order Status",
        }



# =========================================================
# CATEGORY FORM
# =========================================================

class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = [
            "name",
            "description",
            "image",
            "is_active",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Category name",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Category description",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

        }



# =========================================================
# PRODUCT FORM
# =========================================================

class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "category",
            "name",
            "description",
            "image",
            "price",
            "discount_price",
            "stock",
            "is_available",
            "featured",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product name",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Product description",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),

            "discount_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional discount price",
                    "step": "0.01",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0",
                    "min": "0",
                }
            ),

            "is_available": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "featured": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        price = cleaned_data.get("price")
        discount_price = cleaned_data.get(
            "discount_price"
        )

        if (
            discount_price
            and price
            and discount_price >= price
        ):

            self.add_error(
                "discount_price",
                "Discount price must be lower than the regular price."
            )

        return cleaned_data