import os
import subprocess
import whisper
import srt
from tqdm import tqdm

model = whisper.load_model("base")

def transcribe_to_srt(video_path):
    print(f"Processing {video_path}")
    result = model.transcribe(video_path)
    segments = result["segments"]

    subs = []
    for i, seg in enumerate(segments):
        start = seg["start"]
        end   = seg["end"]
        text  = seg["text"].strip()

        subs.append(srt.Subtitle(index=i+1,
                                 start=srt.timedelta(seconds=start),
                                 end  =srt.timedelta(seconds=end),
                                 content=text))
    srt_file = video_path.rsplit(".", 1)[0] + ".srt"
    with open(srt_file, "w") as f:
        f.write(srt.compose(subs))
    return srt_file

def burn_captions(video_path, srt_file):
    out_file = video_path.rsplit(".",1)[0] + "_captions.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_file}",
        "-c:a", "copy",
        out_file
    ]
    subprocess.run(cmd)
    return out_file

def process_folder(folder):
    for file in tqdm(os.listdir(folder)):
        if file.lower().endswith(".mp4"):
            full = os.path.join(folder, file)
            srt_file = transcribe_to_srt(full)
            burn_captions(full, srt_file)

if __name__ == "__main__":
    import sys
    folder = sys.argv[1]
    process_folder(folder)

