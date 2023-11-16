from django.shortcuts import render
from pytube import YouTube
import os

def home(request):
    return render(request, 'home/home.html', {})

def upload_media(request):
    return render(request, 'home/upload_media.html', {})

def select_language(request):
    return render(request, 'home/select_language.html', {})



# 모델예상시간 로딩바 구현하기위한 라이브러리
# case 1 : 웹홈페이지 제공이랑 모델구현(+예상시간)이랑 하나로 합친거
# case 1 문제점 : 모델이 돌아가는 동안 http://loading/ 창 표시를 안함!!!
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tqdm import tqdm
@csrf_exempt
def loading(request):

    # ~~~ 모델 실행 및 예상 시간 계산 로직 추가 ~~~
    # (걸리는 시간만 확인하려고 만든 모델임 나중에 지워도 됨)
    import time
    progress_bar = tqdm(range(10))
    for i in progress_bar:
        time.sleep(1)

    # ~~~ 예상 시간 및 진행률을 클라이언트에게 반환 ~~~
    progress = progress_bar.format_dict['n'] / progress_bar.format_dict['total']  # 현재까지 pqdm이 실행된 n횟수를 반환함
    estimated_time = progress_bar.format_dict['elapsed']  # 예상 시간

    return render(request, 'home/loading.html', {'progress':progress,
                                                 'estimated_tmie':estimated_time,})



# case 2 : 웹홈페이지 제공이랑 모델구현(+예상시간)을 분리

# 웹홈페이지 제공
def loading(request):
    return render(request, 'home/loading.html', {})

# 모델구현 + 예상시간
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tqdm import tqdm
@csrf_exempt
def run_model(request):
    # 모델 실행 및 예상 시간 계산 로직 추가

    # 예상 시간 및 진행률을 클라이언트에게 반환
    response_data = {
        'progress': 50,  # 예시로 50%로 설정
        'estimated_time': '2 hours',  # 예상 시간
    }

    return JsonResponse(response_data)



def select_speaker(request):
    speaker_num = [1, 2, 3]
    return render(request, 'home/select_speaker.html', {'speaker_num': speaker_num})

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
from django.http import JsonResponse

def upload_video(request):
    if request.method == 'POST':
        
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            # 편집 로직을 여기에 추가
            # edited_video_path = edit_video(video.original_video.path)
            # video.edited_video = default_storage.save(edited_video_path, File(edited_video_path))
            video.save()
            return JsonResponse({'success': True, 'video_id': video.id})
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
    if request.method == 'POST':
        context = {'is_youtube_processed': True}
        
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


