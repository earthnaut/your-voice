import sys
import os
from pydub import AudioSegment

task_dir = sys.argv[1]
new_video_path = sys.argv[2]
video_extension = sys.argv[3]

audio_name = "audio_origin.wav"
audio_path = os.path.join(task_dir, audio_name)
audSeg = AudioSegment.from_file(new_video_path, format=video_extension)
audSeg.export(audio_path, format="wav")
