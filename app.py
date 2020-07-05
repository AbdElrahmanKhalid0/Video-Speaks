# trim a video
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# ffmpeg_extract_subclip("video1.mp4", start_time, end_time, targetname="test.mp4")

# open a video
# import os
# os.system("video.mp4")

import srt
from datetime import timedelta
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def make_videos_from_words(word, srt_file_location):
    # opening the subtitle file
    subtitle_file = open(srt_file_location)
    
    # parsing the subtitle file through the srt library
    subtitle_generator = srt.parse(subtitle_file)
    subs = list(subtitle_generator)

    index = 0
    for sub in subs:
        # if the searching word in the current sub
        if word.lower() in sub.content.lower():
            # calculating the share of the word in the sentence or the sub
            word_share_in_content = len(word) / len(sub.content.lower())
            # the index that the word starts in
            word_start = sub.content.lower().find(word.lower())
            # the percentage of the sub that the word starts in
            starting_percentage = word_start / len(sub.content.lower())

            start = sub.start.microseconds / 1000000 + sub.start.seconds
            end = sub.end.microseconds / 1000000 + sub.end.seconds
            time = end - start
            
            # starting from the time that the word starts in
            start += time * starting_percentage - .2

            word_time = time * word_share_in_content
            end = start + word_time + .5

            # making the subtitle for the output video
            sub_for_video = srt.Subtitle(1, start=timedelta(seconds=0), end=timedelta(seconds=end-start), content=word)
            with open(f"{word}{index}.srt", "w") as final:
                final.write(srt.compose([sub_for_video]))
            
            # making the output video
            ffmpeg_extract_subclip("s.mp4", start, end, targetname=f"{word}{index}.mp4")

            index += 1
    
    # closing the srt file
    subtitle_file.close()

make_videos_from_words("hello", "s.srt")