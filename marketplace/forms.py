from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, Comment, Rating, SellerReview


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25) #name of the person sending the product
    email = forms.EmailField() #the email of the person sending the product recommendation.
    to = forms.EmailField() # the email address of the recipient, who will receive an email recommending the product.
    comments = forms.CharField(    #for comments to include in the product recommendation email.
        required=False,    # optional
        widget=forms.Textarea
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    query = forms.CharField()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.RadioSelect(attrs={'class': 'd-inline-block'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].initial = 5


class SellerReviewForm(forms.ModelForm):
    class Meta:
        model = SellerReview
        fields = ['comment', 'rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])
        }