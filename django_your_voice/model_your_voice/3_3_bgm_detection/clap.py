import sys
import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def main():
    task_dir = sys.argv[1]

    # ~~~ pydub이용해 배경음을 무음구간 기준으로 slice하는 과정 ~~~
    input_file_path = sys.argv[2]  # audio_bgm_path
    input_folder_path = os.path.dirname(input_file_path)  # 이게 곧 task_dir 아님?
    os.makedirs(f"{input_folder_path}/bgm_slice")

    # 오디오 파일 로드
    audio = AudioSegment.from_file(input_file_path, format="wav")

    # 무음이 아닌 부분 탐지
    nonsilent_ranges = detect_nonsilent(audio, silence_thresh=-40)

    # 1초 이하와 3초 이상인 부분을 각각 분할
    for i, (start, end) in enumerate(nonsilent_ranges):
        duration = end - start

        less = 3000  # 'less' ms(밀리초) 이하인 부분 분할
        more = 3000  # 'more' ms(밀리초) 이상인 부분 분할

        if duration <= less:
            chunk = audio[start:end]
            chunk.export(
                f"{input_folder_path}/bgm_slice/output_chunk_{start}_{end}_{less}_less.wav",
                format="wav",
            )
        elif duration >= more:
            chunk = audio[start:end]
            chunk.export(
                f"{input_folder_path}/bgm_slice/output_chunk_{start}_{end}_{more}_more.wav",
                format="wav",
            )

    # ~~~ 영 -> 한 변환 라벨 ~~~
    # # 라벨 파일 경로 (.csv)
    label_file_path = "영찬님께 csv파일 받아서 경로 알맞게 수정"
    import csv

    def csv_to_dict(label_file_path):
        result_dict = {}
        with open(label_file_path, "r", newline="",
                  encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # 첫 번째 열을 키로, 두 번째 열을 값으로 하는 딕셔너리 생성
                key = row[0]
                value = row[1]
                if value:  # 값이 비어있지 않은 경우에만 딕셔너리에 추가
                    result_dict[key] = value
        return result_dict

    # 번역 딕셔너리
    trans_label = csv_to_dict(label_file_path)

    # ~~~ clap ~~~
    # 디렉토리 경로 정의 (수정 X)
    dir_path = f"{input_folder_path}/bgm_slice"

    # 디렉토리 내의 WAV 파일만 가져오기
    file_paths = [
        os.path.join(dir_path, file) for file in os.listdir(dir_path)
        if file.lower().endswith(".wav")
    ]

    # clap 메인 코드
    import torchaudio
    from msclap import CLAP
    import numpy as np

    # Load model (Choose version '2023')
    clap_model = CLAP(version="2023", use_cuda=False)

    # 각 fold의 유사성을 저장할 빈 배열 초기화
    all_fold_similarities = []

    # 앙상블 횟수 지정
    ensenble = 5

    # 5-fold ensemble 수행
    for i in range(ensenble):
        # 임베딩
        text_embeddings = clap_model.get_text_embeddings(
            list(trans_label.keys()))
        audio_embeddings = clap_model.get_audio_embeddings(file_paths)

        # 유사도 계산
        similarities = clap_model.compute_similarity(audio_embeddings,
                                                     text_embeddings)

        # 각 fold의 유사성을 저장
        all_fold_similarities.append(similarities)

    # 리스트를 numpy 배열로 변환하여 쉬운 조작을 위해 저장
    all_fold_similarities = np.array(
        [tensor.detach().numpy() for tensor in all_fold_similarities])

    # 각 fold에 대한 유사성의 평균 계산
    average_similarities = np.mean(all_fold_similarities, axis=0)

    # CLAP 결과 리스트 초기화
    result_CLAP = []

    # 결과 출력
    for i, similarity in enumerate(average_similarities):
        max_similarity_index = similarity.argmax()
        max_similarity_value = similarity[max_similarity_index]

        ### 테스트 후, 삭제할 것 ###
        print(max_similarity_value)

        # 폴드 간의 평균 유사성에 대한 임계값 설정
        threshold = 10

        # 유사성이 임계값 이상인 경우에만 캡션 출력
        caption = (list(trans_label.keys())[max_similarity_index]
                   if max_similarity_value >= threshold else "")
        result_sub = file_paths[i].split("\\")[-1]
        result_CLAP.append(f"{result_sub}, {caption}")

    # ~~~ rttm으로 저장 ~~~
    # 파일 불러오기
    file_name = input_file_path.split("/")[-1].split(".")[0]
    folder_output = input_file_path.split("/")[-2]

    # 목록에서 정보 추출하기
    BGM_info_li = []
    for i in result_CLAP:
        start2end = i.split(",")[0].split(".wav")[0].split("/")[-1].split("_")
        start = float(start2end[2])  # 단위: 밀리초
        end = float(start2end[3])
        text = i.split("wav, ")[-1]
        BGM_info_li.append([start, end, text])

    # RTTM 파일로 바꾸기
    result_rttm = ""
    for i in BGM_info_li:
        start = i[0] / 1000  # 단위: 초
        end = i[1] / 1000
        text = i[2]
        duration = end - start

        # 자막이 1초 미만으로 나오면 (너무 빨라서 읽기 어려우므로) 1초로 변경함
        if duration < 1:
            duration = 1

        # 번역
        if text:
            text_trs = trans_label[text]

            result_rttm += f"SPEAKER {file_name} 1 {start} {duration} <NA> <NA> {text_trs} <NA> <NA>\n"

    # 디렉토리 및 하위 파일, 디렉토리 삭제 시도
    import shutil

    shutil.rmtree(dir_path)

    # rttm 저장 (output_folder_path == input_folder_path)
    with open(f"{input_folder_path}/bgm_detection.rttm", "w") as f:
        f.write(result_rttm)

    # 실행예측시간을 txt파일에 계속 업데이트해야하는 코드 (append하는 코드 말고 덮어쓰는 코드로)
    # 각 txt 파일에 업데이트할것 : total , n , elapsed
    # 화면에 보여줄 것
    #   남은 상태바 = sum(n) / sum(total)
    #   남은 시간 = sum(elapsed)


if __name__ == "__main__":
    main()
