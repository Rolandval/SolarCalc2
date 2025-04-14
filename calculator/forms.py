class InverterForm(forms.ModelForm):
    class Meta:
        model = Inverters
        fields = ['brand', 'model', 'power', 'phases_count', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'phases_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class BatteryForm(forms.ModelForm):
    class Meta:
        model = Batteries
        fields = ['brand', 'model', 'capacity', 'is_head', 'is_stand', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'is_head': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_stand': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }class InverterForm(forms.ModelForm):
    class Meta:
        model = Inverters
        fields = ['brand', 'model', 'power', 'phases_count', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'phases_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class BatteryForm(forms.ModelForm):
    class Meta:
        model = Batteries
        fields = ['brand', 'model', 'capacity', 'is_head', 'is_stand', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'is_head': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_stand': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }class InverterForm(forms.ModelForm):
    class Meta:
        model = Inverters
        fields = ['brand', 'model', 'power', 'phases_count', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'phases_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class BatteryForm(forms.ModelForm):
    class Meta:
        model = Batteries
        fields = ['brand', 'model', 'capacity', 'is_head', 'is_stand', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'is_head': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_stand': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }class InverterForm(forms.ModelForm):
    class Meta:
        model = Inverters
        fields = ['brand', 'model', 'power', 'phases_count', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'phases_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class BatteryForm(forms.ModelForm):
    class Meta:
        model = Batteries
        fields = ['brand', 'model', 'capacity', 'is_head', 'is_stand', 'voltage', 'datasheet']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'is_head': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_stand': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'voltage': forms.Select(attrs={'class': 'form-control'}, choices=[('high', 'Висока'), ('low', 'Низька')]),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }