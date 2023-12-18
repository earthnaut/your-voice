import sys
import os


def main():
    print("WISHPER is RUNNING!!!")
    task_dir = sys.argv[1]

    # whisper 모델 다운로드
    import whisper

    try:
        model = whisper.load_model(
            "/home/zisukang0122/.cache/whisper/large-v2.pt",
            device="cuda")  # device = 'cuda' or 'cpu'
    except:
        model = whisper.load_model("large-v2",
                                   device="cuda")  # device = 'cuda' or 'cpu'

    # whisper 모델
    file_path = sys.argv[2]  # audio_path # 자막을 뽑을 오디오 파일 경로
    rttm_file_name = "speech_to_text"  # rttm파일로 저장될 파일명 (확장자명은 자동으로 .rttm 설정)
    # rttm_file_name = "비질란테"

    result = model.transcribe(file_path, word_timestamps=True)

    # ROOT = os.getcwd()
    # pred_rttms_dir = os.path.join(ROOT, "pred_rttms")
    # os.makedirs(pred_rttms_dir, exist_ok=True)
    rttm_file_path = os.path.join(task_dir, f"{rttm_file_name}.rttm")

    with open(rttm_file_path, "w") as file:
        for segment in result["segments"]:
            start = round(segment["start"], 3)
            duration = round(segment["end"] - start, 3)
            speech = segment["text"]

            rttm_line = f"SPEAKER {rttm_file_name} 1 {start} {duration} <NA> <NA> {speech} <NA> <NA>\n"
            file.write(rttm_line)

    # 실행예측시간을 txt파일에 계속 업데이트해야하는 코드 (append하는 코드 말고 덮어쓰는 코드로)
    # 각 txt 파일에 업데이트할것 : total , n , elapsed
    # 화면에 보여줄 것
    #   남은 상태바 = sum(n) / sum(total)
    #   남은 시간 = sum(elapsed)


if __name__ == "__main__":
    main()
