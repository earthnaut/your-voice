from django.shortcuts import render
from pytube import YouTube
import os

def home(request):
    return render(request, 'home/home.html', {})

def upload_media(request):
    return render(request, 'home/upload_media.html', {})

def select_language(request):
    return render(request, 'home/select_language.html', {})

def loading(request):
    return render(request, 'home/loading.html', {})

def select_speaker(request):
    return render(request, 'home/select_speaker.html', {})

def result_download(request):
    return render(request, 'home/result_download.html', {})



# 동영상 편집 로직 구현 (임시!!!)
import subprocess

def edit_video(input_video_path):
    output_video_path = "edited_videos/output.mp4"  # 편집된 동영상의 저장 경로
    # FFmpeg 명령어를 사용하여 동영상 편집
    cmd = f'ffmpeg -i {input_video_path} -vf "your_filter" {output_video_path}'
    subprocess.run(cmd, shell=True)
    return output_video_path



# 동영상 업로드, 편집, 다운로드 기능 처리 (임시!!!)
from django.shortcuts import render, redirect
from django.http import FileResponse
from .models import Video
from .forms import VideoUploadForm
from django.core.files.storage import default_storage

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            # 편집 로직을 여기에 추가
            edited_video_path = edit_video(video.original_video.path)
            video.edited_video = default_storage.save(edited_video_path, File(edited_video_path))
            video.save()
            return redirect('download_video', video_id=video.id)
    else:
        form = VideoUploadForm()
    return render(request, 'home/upload_video.html', {'form': form})

def download_video(request, video_id):
    video = Video.objects.get(id=video_id)
    edited_video = video.edited_video
    response = FileResponse(open(edited_video.path, 'rb'))
    return response



from pytube import YouTube
import os.path
import re

def download_youtube_link(request):
    context = {}

    if request.method == 'POST':
        
        youtube_link = request.POST.get('youtube_link')
        youtube_id_match = re.search(r'(?<=v=)[^&#]+', youtube_link)
        youtube_id_match = youtube_id_match or re.search(r'(?<=be/)[^/&#?]+', youtube_link)
        youtube_id = (youtube_id_match.group(0) if youtube_id_match else None)

        if youtube_id:
            context['thumbnail_url'] = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"

            yt = YouTube(youtube_link)  
            # 비디오 제목, 길이, 파일 크기 추가
            context['title'] = yt.title
            minutes, seconds = divmod(yt.length, 60)
            context['duration'] = f"{minutes}분 {seconds}초"

            path = r'C:\Users\User\Desktop\yourname\your-voice\django_your_voice\videos'  # 다운로드 경로 설정
            yt_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            filesize_mb = yt_stream.filesize / (1024 * 1024)
            context['filesize'] = f"{filesize_mb:.2f} MB"
            
            if not os.path.exists(path):
                os.makedirs(path)
            yt_stream.download(path)

        else:
            context['error'] = '유효하지 않은 YouTube 링크입니다.'

    return render(request, 'home/upload_media.html', context)


