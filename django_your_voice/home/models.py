from django.db import models

# Create your models here.

class Video(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    video_ori = models.FileField(upload_to="uploads/video_ori")
    video_length = models.DurationField() # python의 timedelta형식으로 저장됨
    video_size = models.IntegerField() # 용량 단위 바이트(byte)
    language = models.CharField(max_length=10) # 'ko' (한국어) / 'fo' (외국어)


class Audio(models.Model):
    id = models.AutoField(primary_key=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    audio_ori = models.FileField(upload_to="processing/audio_ori")
    audio_speech = models.FileField(upload_to="processing/audio_speech")
    audio_background = models.FileField(upload_to="processing/audio_background")


class Caption(models.Model):
    id = models.AutoField(primary_key=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    speakers = models.TextField() # 철수;영희;길동; 이런식으로 받기
    caption_speacker = models.FileField(upload_to="results/caption_speacker")
    caption_speech = models.FileField(upload_to="results/caption_speech")
    caption_background = models.FileField(upload_to="results/caption_background")
    caption_combine = models.FileField(upload_to="results/caption_combine")