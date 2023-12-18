from django.shortcuts import render
from pytube import YouTube
import os

import sys
import subprocess

# subprocess 외부에서 새로운 프로세스(지금 실행되는 django 외에 새로운 cpu 단위를 돌리는 거임)를 실행함


def home(request):
    return render(request, "home/home.html", {})


# ~~~ upload_media.html ~~~
def upload_media(request):
    return render(request, "home/upload_media.html", {})


def download_youtube_link(request):
    context = {}
    base_dir = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir,
                            "model_results")

    # 유튜브 저장 루트
    if request.method == "POST":
        # 고유한 task_id 생성 및 파일 저장될 경로 설정
        task_id = str(uuid4())
        task_dir = os.path.join(base_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)

        context = {"is_youtube_processed": True}

        youtube_link = request.POST.get("youtube_link")
        youtube_id_match = re.search(r"(?<=v=)[^&#]+", youtube_link)
        youtube_id_match = youtube_id_match or re.search(
            r"(?<=be/)[^/&#?]+", youtube_link)
        youtube_id = youtube_id_match.group(0) if youtube_id_match else None

        if youtube_id:
            context[
                "thumbnail_url"] = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"

            yt = YouTube(youtube_link)
            # 비디오 제목, 길이, 파일 크기 추가
            context["title"] = yt.title
            minutes, seconds = divmod(yt.length, 60)
            context["duration"] = f"{minutes}분 {seconds}초"

            path = task_dir  # 다운로드 경로 설정
            yt_stream = (yt.streams.filter(
                progressive=True,
                file_extension="mp4").order_by("resolution").desc().first())

            filesize_mb = yt_stream.filesize / (1024 * 1024)
            context["filesize"] = f"{filesize_mb:.2f} MB"

            if not os.path.exists(path):
                os.makedirs(path)
            yt_stream.download(path)

            # # task_id를 쿼리 파라미터로 내보내기 --> HttpResponseRedirect 써야할지 redirect 써야할지 모르겠음
            # # HttpResponseRedirect 사용시
            query_params = urlencode({
                "task_id": task_id,
                "youtube_id": youtube_id
            })
            return HttpResponseRedirect(
                f"/upload-media/youtube/?{query_params}")
            # # redirect 사용시
            # query_params = {'key1': 'value1', 'key2': 'value2'}
            # return redirect('your_next_view', **query_params)
            # # 이때 your_next_view는 django의 url 패턴에 등록된 뷰 이름임! 아 httpresponse 써야겠다!

        else:
            context["error"] = "유효하지 않은 YouTube 링크입니다."

    # 정보 표시 루트
    # task_id로 리다이렉션 되었을 때 할 작업 처리
    # youtube_id를 함께 가져와서 썸네일 사용
    task_id = request.GET.get("task_id")
    if task_id:
        context = {"is_youtube_processed": True}
        # 저장된 video파일에서 정보 추출하기
        task_dir = os.path.join(base_dir, task_id)
        task_name = os.listdir(task_dir)[0]
        task_path = os.path.join(task_dir, task_name)
        task_video = VideoFileClip(task_path)
        context["task_id"] = task_id
        context["title"] = task_name
        context[
            "filesize"] = f"{(os.path.getsize(task_path)  / (1024*1024)):.2f} MB"
        duration_seconds = task_video.duration
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        context["duration"] = f"{int(hours)}시 {int(minutes)}분 {int(seconds)}초"

        # youtube_id에서 썸네일 추출하기
        youtube_id = request.GET.get("youtube_id")
        context[
            "thumbnail_url"] = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"

        # 다음 페이지로 이동하기 위한 쿼리 url
        query_params = urlencode({"task_id": task_id})
        context["next_url"] = f"/select-language/?{query_params}"

        return render(request, "home/upload_media.html", context)

    return render(request, "home/upload_media.html", context)


def download_attachment(request):
    base_dir = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir,
                            "model_results")
    context = {}

    # 첨부파일 저장 루트
    if request.method == "POST":
        context = {"is_attachment_processed": True}
        # 고유한 task_id 생성 및 파일 저장될 경로 설정
        task_id = str(uuid4())
        task_dir = os.path.join(base_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)

        task_file = request.FILES.get("attachment_input")
        if task_file:
            task_extension = task_file.name.split(".")[-1]
            task_name = task_id + task_extension
            task_path = os.path.join(task_dir, task_name)
            # 파일 저장
            with open(task_path, "wb") as f:
                for chunk in task_file.chunks():
                    f.write(chunk)

            query_params = urlencode({"task_id": task_id})
            return HttpResponseRedirect(
                f"/upload-media/attachment/?{query_params}")

    # 정보 표시 루트
    task_id = request.GET.get("task_id")
    if task_id:
        context = {"is_attachment_processed": True}
        # 저장된 video파일에서 정보 추출하기
        task_dir = os.path.join(base_dir, task_id)
        task_name = os.listdir(task_dir)[0]
        task_path = os.path.join(task_dir, task_name)
        task_video = VideoFileClip(task_path)
        context["task_id"] = task_id
        context["title"] = task_name
        context[
            "filesize"] = f"{(os.path.getsize(task_path)  / (1024*1024)):.2f} MB"
        duration_seconds = task_video.duration
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        context["duration"] = f"{int(hours)}시 {int(minutes)}분 {int(seconds)}초"

        # 썸네일 추출 추가해야함
        # task_video.get_frame(5) 사용하기
        # # 비디오 파일 열기
        # clip = VideoFileClip("your_video.mp4")

        # # 5초에 대한 썸네일 가져오기
        # thumbnail_frame = clip.get_frame(5)

        # # 가져온 썸네일을 이미지 파일로 저장하거나 사용할 수 있음
        # thumbnail_frame.save_frame("thumbnail.jpg")

        # 다음 페이지로 이동하기 위한 쿼리 url
        query_params = urlencode({"task_id": task_id})
        context["next_url"] = f"/select-language/?{query_params}"

        return render(request, "home/upload_media.html", context)

    return render(request, "home/upload_media.html", context)


# ~~~ select_language.html ~~~
def select_language(request):
    if request.method == "POST":
        context = {}
        task_id = request.POST.get("task_id")
        if task_id:
            # form으로 받은 정보
            # on일때는 .html에서 input value="on"으로 설정가능한데,
            # 체크박스 해제되어있을 때는 아무 값 전달하지 않으므로 여기에서 설정해야 함
            speech_to_text = request.POST.get("speech_to_text", "off")
            diarization = request.POST.get("diarization", "off")
            bgm_detection = request.POST.get("bgm_detection", "off")
            # 다음 페이지로 이동하기 위한 쿼리 url
            query_params = urlencode({
                "task_id": task_id,
                "stt": speech_to_text,
                "spk": diarization,
                "bgm": bgm_detection,
            })
            context["next_url"] = f"/loading/?{query_params}"
            return HttpResponseRedirect(f"/loading/?{query_params}")

        if not task_id:
            context["next_url"] = f"/invalid_path/"
        return render(request, "home/select_language.html", {})
    return render(request, "home/select_language.html", {})


# 모델예상시간 로딩바 구현
#   POST 요청 --> 모델 실행 및 예상시간 계산
#   GET 요청 --> 단순히 templates 렌더링
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tqdm import tqdm
import time


@csrf_exempt
def loading(request):
    # 모델 프로세스
    if request.method == "GET":
        task_id = request.GET.get("task_id")
        speech_to_text = request.GET.get("stt")
        diarization = request.GET.get("spk")
        bgm_detection = request.GET.get("bgm")

        if task_id:
            # task_id = str(uuid4())
            proc = subprocess.Popen(
                [
                    "python",
                    "model_your_voice/run.py",
                    f"{task_id}",
                    f"{speech_to_text}",
                    f"{diarization}",
                    f"{bgm_detection}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )

            # 자막 3개 다 생성될 때까지 기다림
            # 3개 생성되기 전까지 버튼 안나오게 하고싶음
            proc.wait()

            # subprocess 잘 실행되는지 확인
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                print("오류 발생:", stderr)
            else:
                print("스크립트 실행 결과:", stdout)

    ####################################################################################
    # # run.py가 종료됐는지 확인??? 여기서 확인하는게 맞나??? loading으로 가서 확인해야하는거아님???
    # # if proc.returncode == 0:
    # #     return render(request, 'home/result_download.html', {})
    # # 모델 실행 및 예상 시간 계산 : POST요청
    # if request.method == "POST":
    #     # 이곳에 모델 추가
    #     progress_bar = tqdm(range(60))
    #     for i in progress_bar:
    #         time.sleep(1)  # 단위 (초)

    #     # 예상 시간 및 진행률을 클라이언트에게 반환
    #     # 이거 방법 바꿈!!! 각 모델에서 txt파일로 해당 아래 문구를 생성함
    #     # 그럼 그 텍스트 파일을 실시간으로 받아오는 걸로 바꿈!!!
    #     response_data = {
    #         "progress_percent":
    #         (progress_bar.format_dict["n"] / progress_bar.format_dict["total"])
    #         * 100,  # 'progress':50 --> 예시로 50%로 설정
    #         "estimated_time":
    #         progress_bar.
    #         format_dict["elapsed"],  # 'estimated_time': '2 hours' --> 예상 시간,
    #     }

    #     return JsonResponse(response_data)

    ####################################################################################

    if request.method == "POST":
        context = {}
        task_id = request.GET.get(
            "task_id"
        )  # 아 POST라고 꼭 POST.get 할 필요는 없나봄 .html에 hidden input으로 전달한거 없애도 될듯
        diarization = request.GET.get("spk")
        # 다음 페이지로 이동하기 위한 쿼리 url
        query_params = urlencode({
            "task_id": task_id,
        })
        if diarization == "on":
            context["next_url"] = f"/select-speaker/?{query_params}"
            return HttpResponseRedirect(f"/select-speaker/?{query_params}")
        else:
            context["next_url"] = f"/result-download/?{query_params}"
            return HttpResponseRedirect(f"/result-download/?{query_params}")

    # .html 보여주기 : GET요청
    # proc.communicate()를 쓰면 프로세스 실행이 완료될때까지 기다릴 수 있지만
    # 그러지 않고 프로세스가 완료되지 않아도 즉시 render를 실행함
    return render(request, "home/loading.html", {})


def check_progress(request):
    # txt파일에 적힌 내용을 가져오는 코드
    pass


def select_speaker(request):
    speaker_num = [1]

    if request.method == "POST":
        context = {}
        task_id = request.GET.get("task_id")
        # 다음 페이지로 이동하기 위한 쿼리 url
        query_params = urlencode({
            "task_id": task_id,
        })
        context["next_url"] = f"/result-download/?{query_params}"
        return HttpResponseRedirect(f"/result-download/?{query_params}")

    return render(request, "home/select_speaker.html",
                  {"speaker_num": speaker_num})


def result_download(request):
    task_id = request.GET.get("task_id")  # url 쿼리문에서 GET 해오기
    base_dir = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir,
                            "model_results")
    task_dir = os.path.join(base_dir, task_id)
    download_path = os.path.join(task_dir, "closed_caption.ass")

    # 확장자 포함한 video 파일이름 가져오기
    video_fullname = ""
    for i in os.listdir():
        if "video_origin" in i:
            video_fullname = i
            break
    video_ext = os.path.splitext(video_fullname)
    video_path = os.path.join(task_dir, video_fullname)

    return render(
        request,
        "home/result_download.html",
        {
            "download_path": download_path,
            "video_path": video_path,
            "video_ext": video_ext,
        },
    )


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

# def upload_video(request):
#     if request.method == "POST":
#         form = VideoUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             video = form.save()
#             # 편집 로직을 여기에 추가
#             # edited_video_path = edit_video(video.original_video.path)
#             # video.edited_video = default_storage.save(edited_video_path, File(edited_video_path))
#             video.save()
#             return JsonResponse({"success": True, "video_id": video.id})
#     else:
#         form = VideoUploadForm()
#     return render(request, "home/upload_video.html", {"form": form})

# def download_video(request, video_id):
#     video = Video.objects.get(id=video_id)
#     edited_video = video.edited_video
#     response = FileResponse(open(edited_video.path, "rb"))
#     return response

from pytube import YouTube
from moviepy.editor import VideoFileClip
import os.path
import re

from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.shortcuts import redirect
from uuid import uuid4  # uuid4는 무작위로 생성된 고유한 식별자(UUID)를 반환, 객체를 고유하게 식별하기 위한 용도

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


# 작동 원리
# 웹 /upload-media/에서 youtube링크 제출을 누름
# --> 폼을 제출하면 .html에서 action="{% url 'download_youtube_link' %}"가 작동됨
# --> views.download_youtube_link가 돌아감
# --> POST 요청이 왔으니 유튜브 저장 루트가 돌아감
# --> 리턴으로 '/upload-media/youtube/?{query_params}'를 반환함 (이때 task_id와 youtube_id를 쿼리로 함께 전달)
# --> urls.py에 /upload-media/youtube/로 연결된 views.download_youtuve_link가 한번 더 실행됨
# --> task_id가 있을 경우, 정보 표시 루트가 돌아감
# --> .html에서 {% if task_id %} 가 돌아가며 썸네일과 정보 등을 함께 표시함


def invalid_path(request):
    return render(request, "invalid_path.html", {})
