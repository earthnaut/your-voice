from django.shortcuts import render
from pytube import YouTube
import os


import sys
import subprocess
# subprocess 외부에서 새로운 프로세스(지금 실행되는 django 외에 새로운 cpu 단위를 돌리는 거임)를 실행함


def home(request):
    return render(request, 'home/home.html', {})

def upload_media(request):
    return render(request, 'home/upload_media.html', {})





from uuid import uuid4
# uuid4는 무작위로 생성된 고유한 식별자(UUID)를 반환, 객체를 고유하게 식별하기 위한 용도

def select_language(request):
    print("A")

    # 모델 프로세스
    task_id = str(uuid4())
    proc = subprocess.Popen(['python', '/model_your_voice/run.py', f"{task_id}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # proc.communicate()를 쓰면 프로세스 실행이 완료될때까지 기다릴 수 있지만
    # 그러지 않고 프로세스가 완료되지 않아도 즉시 render를 실행함

    # run.py가 종료됐는지 확인??? 여기서 확인하는게 맞나??? loading으로 가서 확인해야하는거아님???
    # if proc.returncode == 0:
    #     return render(request, 'home/result_download.html', {})
    
    return render(request, 'home/select_language.html', {})



# 모델예상시간 로딩바 구현
#   POST 요청 --> 모델 실행 및 예상시간 계산
#   GET 요청 --> 단순히 templates 렌더링
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tqdm import tqdm
import time

@csrf_exempt
def loading(request):

    # 모델 실행 및 예상 시간 계산 : POST요청
    if request.method == 'POST':

        # 이곳에 모델 추가
        progress_bar = tqdm(range(60))
        for i in progress_bar:
            time.sleep(1) # 단위 (초)

        # 예상 시간 및 진행률을 클라이언트에게 반환
        # 이거 방법 바꿈!!! 각 모델에서 txt파일로 해당 아래 문구를 생성함
        # 그럼 그 텍스트 파일을 실시간으로 받아오는 걸로 바꿈!!!
        response_data = {
            'progress_percent': (progress_bar.format_dict['n'] / progress_bar.format_dict['total']) * 100 ,  # 'progress':50 --> 예시로 50%로 설정
            'estimated_time': progress_bar.format_dict['elapsed'],  # 'estimated_time': '2 hours' --> 예상 시간,
        }

        return JsonResponse(response_data)
    # .html 보여주기 : GET요청
    return render(request, 'home/loading.html', {})



def check_progress(request):
    # txt파일에 적힌 내용을 가져오는 코드
    pass



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

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            # 편집 로직을 여기에 추가
            # edited_video_path = edit_video(video.original_video.path)
            # video.edited_video = default_storage.save(edited_video_path, File(edited_video_path))
            video.save()
            return redirect('loading', video_id=video.id)
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

from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.shortcuts import redirect

# 1. 고유 ID 만들어서 유튜브 저장 경로시 해당 ID 경로로 저장하게끔 하기
#   task_id = str(uuid4())
#   base_dir = os.path.join(os.path.abspath(__file__), '../model_results')
#   task_dir = os.path.join(base_dir, task_id)
# 2. 고유 ID를 세션에 저장해서 ID 정보를 기억하기 --> 보안상 문제있음
#   request.session['task_id'] = task_id
# 3. 고유 ID를 url 쿼리 파라미터에 저장해서 ID 정보를 기억하기
#   URL(views.py의 your_next_view함수)로 이동하면서 쿼리 매개변수 전달
#       def your_view(request):
#       return redirect('your_next_view', task_id=task_id)
#   그럼 함수 your_next_view에서 task_id를 같이 받을 수 있음!
#       def your_next_view(request, task_id):

def task_id_generate(request):
    pass


def download_youtube_link(request):
    context = {}

    if request.method == 'POST':
        # 고유한 task_id 생성 및 파일 저장될 경로 설정
        task_id = str(uuid4())
        base_dir = os.path.join(os.path.abspath(__file__), '../model_results')
        task_dir = os.path.join(base_dir, task_id)

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

            path = task_dir  # 다운로드 경로 설정
            yt_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            filesize_mb = yt_stream.filesize / (1024 * 1024)
            context['filesize'] = f"{filesize_mb:.2f} MB"
            
            if not os.path.exists(path):
                os.makedirs(path)
            yt_stream.download(path)

            # task_id를 쿼리 파라미터로 내보내기 --> HttpResponseRedirect 써야할지 redirect 써야할지 모르겠음
            # HttpResponseRedirect 사용시
            query_params = urlencode({'task_id': task_id})
            return HttpResponseRedirect(f'/upload_media/?{query_params}')
            # redirect 사용시
            query_params = {'key1': 'value1', 'key2': 'value2'}
            return redirect('your_next_view', **query_params)
            # 이때 your_next_view는 django의 url 패턴에 등록된 뷰 이름임! 아 httpresponse 써야겠다!

        else:
            context['error'] = '유효하지 않은 YouTube 링크입니다.'

    return render(request, 'home/upload_media.html', context)


