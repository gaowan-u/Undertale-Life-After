#!/bin/bash

input_file="/storage/emulated/0/传说之下-劫后余生/audios/test.ogg"
output_file="/storage/emulated/0/传说之下-劫后余生/audios/test_cut.ogg"

# 分割音频 (4-5秒)
ffmpeg -i "$input_file" -ss 8.5 -to 9 -c copy "$output_file" -y

echo "分割完成! 输出文件: $output_file"