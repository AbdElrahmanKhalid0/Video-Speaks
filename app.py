# trim a video
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# ffmpeg_extract_subclip("video1.mp4", start_time, end_time, targetname="test.mp4")

# open a video
# import os
# os.system("video.mp4")

import srt
import os
import re
from datetime import timedelta
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


class Movie:
    def __init__(self, directory_title, path, subtitle):
        self.setAttributes(directory_title)
        self.path = path
        self.subtitle = subtitle

    # this function should differ for every set of movies names and it's only use is for
    # prettifying the movie data
    def setAttributes(self, directory_title):
        self.title = directory_title[:directory_title.find("(")].strip()
        self.year = directory_title[directory_title.find("(") + 1 : directory_title.find(")")]

        # the movie folder title is not in the format "MOVIE_NAME (YEAR)"
        if directory_title.find("(") == -1:
            directory_title = directory_title.replace("."," ")
            match = re.search("\d",directory_title)
            # assuming that the first digital number is the year and it is consisting of 4 digits
            if match is not None:
                self.title = directory_title[:match.span()[0]].strip()
                self.year = directory_title[match.span()[0]:match.span()[0] + 4]
            else:
                self.title = directory_title
                self.year = None

    def __repr__(self):
        # return f"{self.title} | {self.year}"
        return str(self.subtitle)


def load_data(movies_location, subtitles_location = ""):
    # the location should contain movies folders and in every folder is a subtitle with
    # the movie itself but in case there is a subtitles_location it will be the location
    # of all the subtitles
    os.chdir(movies_location)

    movies = []
    for f in os.scandir():
        if not f.is_dir():
            continue

        location = os.path.join(movies_location ,f.name)
        os.chdir(location)
        
        # getting the first file with "mp4" or "mkv" extension
        movie_file = [f for f in os.listdir() if ".mp4" in f or ".mkv" in f][0]
        # assuming that the subtitle is the same name as the movie
        subtitle = movie_file.replace(".mkv",".srt").replace(".mp4",".srt")
        
        # adding the movie to the movies list
        movies.append(Movie(f.name, rf"{location}\{movie_file}",{"subtitle": subtitle, "location":location if not subtitles_location else subtitles_location}))
    
    return movies
   

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


def search_in_subtitles(phrase ,movies):
    for movie in movies:
        try:
            subtitle_file = open(rf"{movie.subtitle['location']}\{movie.subtitle['subtitle']}", "r")
            subtitle_generator = srt.parse(subtitle_file)

            subs = list(subtitle_generator)
            for sub in subs:
                if phrase.lower() in sub.content.lower():
                    return {"sub":sub, "path":movie.path}
        except:
            continue


def main():
    movies = load_data(r"path\to\movies", r"path\to\subtitles")
    print(search_in_subtitles("batman", movies))
    # make_videos_from_words("hello", "s.srt")


if __name__ == "__main__":
    main()