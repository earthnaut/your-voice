from django import forms

# 동영상 업로드하기 위한 폼 (임시!!!)
from .models import Video
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['video_ori']