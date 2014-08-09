# -*- coding: utf-8 -*-

### Key Bindings ###
keys=(
    ("q"             , "close"),
    ("Right"         , "smartRight"),
    ("Left"          , "smartLeft"),
    ("Up"            , "smartUp"),
    ("Down"          , "smartDown"),
    ("PgDown"        , "nextImage"),
    ("PgUp"          , "prevImage"),

    # Emacser
    ("Alt+p"         , "prevImage"),
    ("Alt+n"         , "nextImage"),
    ("n"             , "smartDown"),
    ("p"             , "smartUp"),
    ("f"             , "smartRight"),
    ("b"             , "smartLeft"),
    ("Ctrl+d"        , "deleteFile"),
    
    ("Ctrl+v"        , "nextImage"),
    ("Alt+v"         , "prevImage"),
    ("Ctrl+x Ctrl+c" , "close"),

    # Vimer
    ("l"             , "smartRight"),
    ("h"             , "smartLeft"),
    ("k"             , "smartUp"),
    ("j"             , "smartDown"),

    
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
    ("f2"       , "renameFile"),
)

### Behavior of mouse scrolling, 'Navigate' or 'Zoom'

mouseWheelBehavior='Zoom'

### Default values after startup. ###

# If remember zoom mode after switching picture.
rememberZoomMode=False

# If show the information labels of picture.
ifShowInfoLabels=True

# If show the status labels.
ifShowStatusLabels=False

# Sort by 'Name' or 'Time'.
sortBy='Name'

