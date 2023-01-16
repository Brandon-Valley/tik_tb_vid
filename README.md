# tik_tb_vid

pip install moviepy

pip install cv2

pip install ffmpeg-python

https://pjreddie.com/media/files/yolov3.weights

pip install opencv-python
pip install opencv-contrib-python


# playlist dl test
pip install bs4
pip install PyQtWebEngine
pip install pytube

# subtitle

pip install pvleopard

# Probably answer for yt dl but needs api key
- https://www.geeksforgeeks.org/download-youtube-videos-or-whole-playlist-with-python/
- - https://www.4kdownload.com/-1uvr6/video-downloader
- 



pip install --upgrade google-api-python-client

pip install --upgrade google-auth-oauthlib google-auth-httplib2

api key in email/drive



transcript site from HackerNews, saw some CLI thing - https://youtubetranscript.com/

fiver clips: https://www.fiverr.com/wabzee/make-short-form-family-guy-clips-for-you-to-post?context_referrer=search_gigs&source=top-bar&ref_ctx_id=9d3579a52d0159c603723dafad38221b&pckg_id=1&pos=1&context_type=auto&funnel=9d3579a52d0159c603723dafad38221b&imp_id=dd236ce3-6902-4516-b8cd-98dc083e74bf

https://vlipsy.com/search/Family%20Guy/6 







https://www.instagram.com/petergriffin/?hl=en



Split video by chapters: Videos can be split into multiple files based on chapters using --split-chapters


pip install --pre ttconv


https://www.solveigmm.com/en/howto/how-to-edit-video-files-with-subtitles-with-video-splitter/

https://codecguide.com/download_other.htm



https://www.videohelp.com/software/VideoReDo

https://forum.videohelp.com/threads/359121-How-to-extract-cut-parts-from-a-mkv-including-all-audio-and-subtitle-tracks

https://www.videohelp.com/software/sections/video-editors-basic

# Manual vid edit with embedded subtitles

## Setup

- make subs play by default
  - From: https://codecs.forumotion.net/t3018-subtitles-default-question
    - MPC-HC options > Playback > Default Track Preference > Subtitles > 1

## Usage
- MKVToolNix
  - split mode by parts

- media viewer classic
  - ctrl + G
  - ctrl + <>
  - ctrl + F3 for custom ahk to get cur time


# SUB match

- https://forum.opensubtitles.org/viewtopic.php?t=16826
- googled: opensubtitles.org family guy series overview
- https://www.opensubtitles.org/en/ssearch/sublanguageid-all/idmovie-7533

- https://www.opensubtitles.org/en/ssearch/sublanguageid-eng/idmovie-7533
- - ^^ googled opensubtitles.org family guy series overview english subtitles

pip install pysubs2

<!-- pip install fuzzysearch -->

pip install fuzzywuzzy
<!-- pip install ffsubsync -->
pip install autosubsync
pip3 install subnuker
pip install aeidon
install python-levenshtein

# Good test caused
- herbert clip - s4 e16 - The Courtship of Stewie's Father
  - short 30 seconds
  - not much dialog
  - awful auto subs
  - top en subtitle broke stuff b/c it starts with many empty
  - have a spanish sub in dir for some reason
- mcstroke - very hard to understand voice, makes it through every episode without getting fuzz_str > 0
- Google earth
  - got wrong subs, should be C:\p\tik_tb_vid_big_data\ignore\subs\fg\og_bulk_sub_dl_by_season\en\s10\episode 20
  - S01E04__Family_Guy__Google_Earth__Clip____TBS.mkv
- S10E20 - in
serted extra subs
  - "C:\p\tik_tb_vid_big_data\ignore\subs\fg\og_bulk_sub_dl_by_season\en\s10\episode 20\Family.Guy.S10E20.720p.HDTV.X264-DIMENSION.srt"
  - == sync, corrected by <font color="#00ff00">elderman</font> ==
- S5E17 - also got random modern family subs for some reason
- S6E1 - Blue Harvest - Star wars
  - long clip with lots of silence
  - has labeled directors comment and hearing impaired and fps
  - has UN LABELED wrong fps
  - has UN LABELED extended edition
      - In yt clip he just says "what if they come in a different door"?
          - in extended edition they argue about running to a different door
          - Was able to match right episode from extended edition subs, but messed up re-timing/syncing
- S10E20 - Peter joins the Tea Party
    - has .hi. subs with "gasps", "cheers", etc. that if chosen, mess up autosubsync
    - even the .LOL.srt is slightly off for some reason?
    - choosing the smallest "nice" sub file makes it pick .DEMAND. which matches perfectly

- S8E20 - Something, Something, Something Darkside
    - Star wars special
    - has part1&2 subs even though they are different episodes

- S15E13 - fuzz str 53 char long (max is 22922)

- S1E1 - really bad case for trim/re-time sub time wehe

# Steps

1. dl real subs for whole series
2. download yt playlist with youtube_utils.dl_yt_playlist__fix_sub_times_convert_to__mp4_srt()
3. get_init_mkvs_for_manual_edits.py (can be combined with ^^)
   1. init clean fresh downloads
   2. run rest of main
      1. This will make dir of mkvs ready for manual editing
4. manual editing
   1. See *Manual vid edit with embedded subtitles* above






https://superuser.com/questions/1734087/how-to-do-automatically-transfer-subtitles-from-one-video-to-another-based-on - It take a subtitle and related frame from movie A and search the best matching frame in movie B. Once it find it, it adjust subtitle timings accordingly (it proceed like that for every subtitle). The search is limited to a certains number of frames in forward and backward direction. it over to a 2:30 hours movie (which contains many small differences with reference movie and over 2000 subtitles) and it worked very well.