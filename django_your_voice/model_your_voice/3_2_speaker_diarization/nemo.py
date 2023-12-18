import sys
import os


def main():
    task_dir = sys.argv[1]

    # ~~~ pre-emphasis ~~~
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import librosa
    import librosa.display
    import torch
    import torchaudio
    import IPython.display as ipd
    import os
    import scipy.io.wavfile as wavf

    # 파일 불러오기
    file_path_ori = sys.argv[2]  # audio_path
    file_dir, file_pullname = os.path.split(file_path_ori)
    file_name, file_ext = os.path.splitext(file_pullname)
    waveform_ori, sample_rate_ori = librosa.load(file_path_ori,
                                                 sr=None)  # numpy array

    # 노멀라이징
    norm_waveform_ori = librosa.util.normalize(waveform_ori)

    # pre-emphasis 적용
    pre_emphasized_ori = np.append(
        norm_waveform_ori[0],
        norm_waveform_ori[1:] - 0.97 * norm_waveform_ori[:-1])
    # 0.97 = pre_emphasis_coefficient 얼만큼 강하게 고주파 강화 할 것인지

    # 저장
    pre_emphasized_path = os.path.join(task_dir, "audio_preemphasized.wav")
    wavf.write(pre_emphasized_path, sample_rate_ori, waveform_ori)

    # ~~~ nemo ~~~
    import nemo.collections.asr as nemo_asr
    import numpy as np
    from IPython.display import Audio, display
    import librosa
    import os
    import wget
    import matplotlib.pyplot as plt

    import nemo
    import glob

    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    from pydub import AudioSegment
    from nemo.collections.asr.models.msdd_models import NeuralDiarizer
    from omegaconf import OmegaConf
    import shutil

    import librosa
    import scipy.io.wavfile as wavf
    import json

    # wav 파일 경로 입력
    file_path = pre_emphasized_path

    # 저장될 rttm 파일명 입력
    file_name = "speaker_diarization"

    # 화자수 입력 (설정 안하면 모델이 파악)
    num_speakers = None

    # 최대 화자수 입력(기본값 8)
    max_num_speakers = 8

    ################################################
    DOMAIN_TYPE = "telephonic"
    device = "cuda"  # 'cpu' or 'cuda'
    rttm_filepath = os.path.join(
        task_dir, "speech_to_text.rttm"
    )  # 이 값에 rttm 경로 주면 whisper rttm으로 VAD 사용, 안쓸땐 None
    ################################################

    # 오디오파일의 채널 파악 후 channel 1로 변환
    if AudioSegment.from_file(file_path).channels != 1:
        mono_sound = AudioSegment.from_file(file_path).set_channels(1)
        ROOT = os.getcwd()
        mono_sound_path = os.path.join(ROOT, "mono_sound")
        os.makedirs(mono_sound_path, exist_ok=True)
        mono_sound.export(os.path.join(mono_sound_path,
                                       f"{file_name}_mono.wav"),
                          format="wav")
        mono_file_path = f"./mono_sound/{file_name}_mono.wav"
    else:
        mono_file_path = file_path

    ROOT = os.getcwd()
    data_dir = os.path.join(ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)

    CONFIG_FILE_NAME = f"diar_infer_{DOMAIN_TYPE}.yaml"

    CONFIG_URL = f"https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/{CONFIG_FILE_NAME}"

    if not os.path.exists(os.path.join(data_dir, CONFIG_FILE_NAME)):
        CONFIG = wget.download(CONFIG_URL, data_dir)
    else:
        CONFIG = os.path.join(data_dir, CONFIG_FILE_NAME)

    cfg = OmegaConf.load(CONFIG)
    # print(OmegaConf.to_yaml(cfg))

    # Create a manifest file for input with below format.
    # {"audio_filepath": "/path/to/audio_file", "offset": 0, "duration": null, "label": "infer", "text": "-",
    # "num_speakers": null, "rttm_filepath": "/path/to/rttm/file", "uem_filepath"="/path/to/uem/filepath"}
    import json

    meta = {
        "audio_filepath": mono_file_path,
        "offset": 0,
        "duration": None,
        "label": "infer",
        "text": "-",
        "num_speakers": num_speakers,
        "rttm_filepath": rttm_filepath,
        "uem_filepath": None,
    }
    with open(os.path.join(data_dir, "input_manifest.json"), "w") as fp:
        json.dump(meta, fp)
        fp.write("\n")

    cfg.diarizer.manifest_filepath = os.path.join(data_dir,
                                                  "input_manifest.json")
    cfg.num_workers = 0

    pretrained_speaker_model = "titanet_large"
    cfg.diarizer.manifest_filepath = cfg.diarizer.manifest_filepath
    cfg.diarizer.out_dir = (
        data_dir  # Directory to store intermediate files and prediction outputs
    )
    cfg.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
    cfg.diarizer.clustering.parameters.oracle_num_speakers = False

    # Using Neural VAD and Conformer ASR
    cfg.diarizer.vad.model_path = "vad_multilingual_marblenet"
    cfg.diarizer.asr.model_path = "stt_en_conformer_ctc_large"
    cfg.diarizer.oracle_vad = False  # ----> Not using oracle VAD # 태연언니:
    cfg.diarizer.asr.parameters.asr_based_vad = False
    cfg.diarizer.clustering.parameters.max_num_speakers = max_num_speakers

    ###########################################################
    if num_speakers:
        cfg.diarizer.clustering.parameters.oracle_num_speakers = True

    if rttm_filepath:
        cfg.diarizer.oracle_vad = True
        cfg.diarizer.asr.parameters.asr_based_vad = True
    ###########################################################

    cfg.device = device
    msdd_model = NeuralDiarizer(cfg)
    msdd_model.diarize()

    # 실행예측시간을 txt파일에 계속 업데이트해야하는 코드 (append하는 코드 말고 덮어쓰는 코드로)
    # 각 txt 파일에 업데이트할것 : total , n , elapsed
    # 화면에 보여줄 것
    #   남은 상태바 = sum(n) / sum(total)
    #   남은 시간 = sum(elapsed)


if __name__ == "__main__":
    main()
