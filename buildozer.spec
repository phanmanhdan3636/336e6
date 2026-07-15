[app]
title = Pixel Gunsmith
package.name = pixelgunsmith
package.domain = org.mygame
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,otf,json,wav,mp3,ogg,atlas
version = 0.1
requirements = python3,pygame-ce
orientation = landscape
fullscreen = 1
android.permissions = VIBRATE
# Keep logs smaller / simpler
log_level = 2
android.accept_sdk_license = True
android.skip_update = False
[buildozer]
warn_on_root = 0

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
