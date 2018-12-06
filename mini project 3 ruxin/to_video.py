def to_video():
    import os
    os.system('ffmpeg -r 1/3 -f image2 -i pictures\%d.jpg -s 800x600 twittervideo.mp4')