from django import forms
from django.core.validators import RegexValidator

class CheckoutForm(forms.Form):
    # Phone number ke liye validator (Taaki sirf 10 digits hi allow hon)
    phone_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number 10 digits ka hona chahiye (e.g. 9876543210)."
    )

    full_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )

    phone = forms.CharField(
        validators=[phone_regex],
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-Digit Mobile Number'})
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'House No, Building, Street Name'})
    )

    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )

    pincode = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode (6 Digits)'})
    )

    # Optional: Payment Method choose karne ke liye
    PAYMENT_CHOICES = [
        ('UPI', 'Online (UPI/QR Scan)'),
        ('COD', 'Cash on Delivery'),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    # Pincode validate karne ke liye custom function
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            raise forms.ValidationError("Kripya sahi 6-digit Pincode bharein.")
        return pincode