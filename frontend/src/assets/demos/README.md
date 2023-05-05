FFMPEG command to compress:

`ffmpeg -i input.mp4 -c:v libx264 -preset fast -r 30 -vf "scale=480:-1" -c:a copy output.mp4`
