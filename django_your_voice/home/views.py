from django.shortcuts import render

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
    return render(request, 'upload_video.html', {'form': form})

def download_video(request, video_id):
    video = Video.objects.get(id=video_id)
    edited_video = video.edited_video
    response = FileResponse(open(edited_video.path, 'rb'))
    return response

