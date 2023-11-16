import sys
import os
import subprocess
from pydub import AudioSegment

base_dir = os.path.join(os.path.abspath(__file__), '../model_results')
# os.path.abspath(__file__) 현재 스크립트의 절대 경로
# os.path.join(...) 여러 경로를 안전하게 결합해주는 함수

def main(task_id):
    task_dir = os.path.join(base_dir, task_id)
    # os.makedirs(task_dir, exist_ok=True)
    # 이미 영상 다운로드 받는 과정에서 만들어지는 폴더여서 주석처리함

    # 1번 2번은 이 run.py에 작성하고, 3번은 각각 .py 만들어서 subprocess로 동시진행 (비동기진행) 하도록 함

    # 0. 비디오 파일명을 유튜브 제목 -> task_id로 변경
    video_name = os.listdir(task_dir)[0] # 여기에 '강아지.mp4' 이렇게 확장자 같이 들어가겠지?
    video_extension = video_name.split['.'][0]
    new_video_name = task_id + '.' + video_extension
    old_video_name_path = os.path.join(task_dir, video_name)
    new_video_name_path = os.path.join(task_dir, new_video_name)
    os.rename(old_video_name_path, new_video_name_path)
    
    # 1. mp4 -> 음원파일로 변경 
    task_audio_dir = os.path.join(task_dir, 'audio')
    os.makedirs(task_audio_dir, exist_ok=True)

    # convert mp4에서 wav파일로 변환
    audio_name = task_id + '.wav'
    audio_path = os.path.join(task_audio_dir, audio_name)
    audSeg = AudioSegment.from_file(new_video_name_path, format=video_extension)
    audSeg.export(audio_path, format="wav")

    # 2. 음원 -> (배경, 음성) 분리 os.path.join(task_dir, 'bgm'), os.path.join(task_dir, 'speech')
    # 3. 태스크 진행 (비동기로 동시진행함)
    #   3-1. 자막생성 os.path.join(task_dir, 'speech_to_text')
    proc_1 = subprocess.Popen(['python', '/model_your_voice/model_speech_to_text.py', f"{task_id}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #   3-2. 화자분리 os.path.join(task_dir, 'speaker_diarization')
    proc_2 = subprocess.Popen(['python', '/model_your_voice/model_speaker_diarization.py', f"{task_id}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #   3-3. 배경음악이벤트추출 os.path.join(task_dir, 'bgm_detection')
    proc_3 = subprocess.Popen(['python', '/model_your_voice/model_bgm_detection.py', f"{task_id}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # 4. 자막 합치기
        # 만약에 1, 2, 3이 모두 끝났으면
    # if proc_1 == 0 and proc_2 == 0 and proc_3 == 0:
    #     pass        
    # 이거 쓰지 말라고 하셨음!!!
    # 따로 txt를 만들어서 세개 모두 끝났을 때 txt에 done이 입력되도록 만들면
    # ajax가 done을 인식해서 만약 done일때 다음 템플릿으로 넘어감
    

if __name__ == '__main__':
    main(sys.args[2])
    # args는 ['python', '/mymodel/run.py', f"{task_id}"]중에 두번째인 task_id를 받아옴!



