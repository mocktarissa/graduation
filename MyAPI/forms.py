from django.forms import ModelForm
from . models import predictions

class MyForm(ModelForm):
	class Meta:
		model=predictions
		fields = '__all__'
		#exclude = 'firstname'