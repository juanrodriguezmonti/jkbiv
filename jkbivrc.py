# -*- coding: utf-8 -*-

# Key Bindings
####################################################################

keys=(
    ("q"             , "close"),
    ("Esc"           , "close"),
    ("Right"         , "smartRight"),
    ("Left"          , "smartLeft"),
    ("Up"            , "smartUp"),
    ("Down"          , "smartDown"),
    ("PgDown"        , "nextImage"),
    ("PgUp"          , "prevImage"),

    # Emacser
    ("Ctrl+v"        , "nextImage"),
    ("Alt+v"         , "prevImage"),
    ("Alt+n"         , "nextImage"),
    ("Alt+p"         , "prevImage"),
    
    ("n"             , "smartDown"),
    ("p"             , "smartUp"),
    ("f"             , "smartRight"),
    ("b"             , "smartLeft"),
    
    ("Ctrl+x, Ctrl+c", "close"),
    ("Ctrl+x, k"     , "close"),
    ("Shift+d"       , "deleteFile"),
    ("Ctrl+x, Ctrl+q", "renameFile"),
    ("Alt+w"         , "copyFilePath"),
    ("Ctrl+c, d"     , "duplicateWindow"),
    
    ("!"             , "runShellCommandSynchronously"),
    ("&"             , "runShellCommand"),
    

    # Vimer
    ("l"             , "smartRight"),
    ("h"             , "smartLeft"),
    ("k"             , "smartUp"),
    ("j"             , "smartDown"),
    ("y, y"          , "duplicateWindow"),
    ("@"             , "copyFilePath"),

    
    ("s"             , "sortSwitcher"),
    ("Shift+f"       , "toggleFullScreen"),
    ("="             , "zoomIn"),
    ("-"             , "zoomOut"),
    ("1"             , "origianlSize"),
    ("w"             , "fitToWindow"),
    ("r"             , "toggleRememberZoomMode"),
    ("Shift+Right"   , "scrollRight"),
    ("Shift+Left"    , "scrollLeft"),
    ("Shift+Up"      , "scrollUp"),
    ("Shift+Down"    , "scrollDown"),
    ("i"             , "toggleInfoLabels"),
    ("Shift+i"       , "toggleStatusLabels"),
    ("f2"            , "renameFile"),
    ("Shift+n"       , "duplicateWindow"),
)

# Behavior of mouse scrolling, 'Navigate' or 'Zoom'
####################################################################

mouseWheelBehavior='Navigate'

# Default values after startup.
####################################################################
# Fullscreen after startup
fullScreen=False

# Default window size
width=640
height=480

# If remember zoom mode after switching picture.
rememberZoomMode=False

# If show the information labels of picture.
ifShowInfoLabels=True

# If show the status labels.
ifShowStatusLabels=False

# Sort by 'Name' or 'Time'.
sortBy='Name'


