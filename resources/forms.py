import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Resource

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
    '.zip', '.rar', '.7z', '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif',
    '.mp4', '.mp3',
}

# 单个文件大小上限（字节），这里设为 50MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'category', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 编辑时文件可选（留空则不修改原文件），上传时仍必须传文件
        if self.instance and self.instance.pk:
            self.fields['file'].required = False
            self.fields['file'].help_text = '不修改文件可留空'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'不支持的文件类型「{ext}」。'
                '允许：PDF、Word、PPT、Excel、压缩包、图片、文本、音视频等。'
            )
        if file.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('文件不能超过 50MB。')
        return file


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='邮箱', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
