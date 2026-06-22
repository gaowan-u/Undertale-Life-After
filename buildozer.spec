[app]

title = 传说之下-劫后余生
package.name = undertalelifeafter
package.domain = org.undertale.fan

source.dir = .
source.include_exts = py,png,jpg,ogg,ttf,wav,mp3,mp4

version = 0.1

requirements = python3==3.11.15,pygame

orientation = landscape
fullscreen = 1

presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 20
android.archs = arm64-v8a, armeabi-v7a

android.permissions =
android.wakelock = False
android.allow_backup = True

android.accept_sdk_license = True

p4a.bootstrap = sdl2

[buildozer]

log_level = 2
warn_on_root = 0
