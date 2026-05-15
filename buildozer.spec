[app]
title = AURA Semantic Core
package.name = aura_semantic_core
package.domain = com.tfrank42
source.dir = .
source.include_exts = py,bin
source.include_patterns = aura_semantic_core.py,main.py,aura_brain.bin
version = 1.0.0
requirements = python3,kivy==2.3.0
p4a.branch = v2023.09.16
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
