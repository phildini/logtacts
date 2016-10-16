from django import forms


class PaymentForm(forms.Form):

    stripeTokenType = forms.CharField(required=False)
    stripeEmail = forms.EmailField(required=False)
    stripeToken = forms.CharField(required=True)
