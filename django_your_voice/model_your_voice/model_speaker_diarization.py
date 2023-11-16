import sys
import os

base_dir = os.path.join(os.path.abspath(__file__), '../model_results')

def main(task_id):
    task_dir = os.path.join(base_dir, task_id)

    #   3-2. 화자분리
    task_model3_dir = os.path.join(task_dir, 'speaker_diarization')
    os.makedirs(task_model3_dir, exist_ok=True)
    
    # 실행예측시간을 txt파일에 계속 업데이트해야하는 코드 (append하는 코드 말고 덮어쓰는 코드로)
    # 각 txt 파일에 업데이트할것 : total , n , elapsed
    # 화면에 보여줄 것
    #   남은 상태바 = sum(n) / sum(total)
    #   남은 시간 = sum(elapsed)

    pass
    

if __name__ == '__main__':
    main(sys.args[2])



