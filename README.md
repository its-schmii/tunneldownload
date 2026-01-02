
> Download your Tunn3l-Media-Files-Video files to a ./media folder

Files are saved with the following format:  
{YYMMDD}-{HH}_{MM}-{Session Nr}-{Camera perspective}.mp4  
under the folder {YYMMDD}/{HH}_{MM}/  


I wrote this script for downloading videos at Fööni (https://www.fööni.de)  
It should theoretically be easily changable for any Tunnel using Tunn3l as their software as long as  you change the URL in download.py

Disclaimer:  
- this is a one hour hack project. If Tunn3l changes their interface nothing works (duh!)  
- Python is not my first language, if it's not the python way (TM) somewhere feel free to ignore it or make a PR so I can learn something  
- Use at your own risk.

If anybody wants to contribute (more Output, include login, configure URLs etc pp) feel free to do so and make a PR.


### Usage:
Before using download.py create a cookie_file with your login-cookie.

Example cookie-file:
Tunn3lMedia=xxxxxxxxxxxxxxxxxxxx

With no arguments it will download all perspectives for the last 30 days.  
Be nice about your tunnels bandwith and consider if you really want all perspectives, or if Bottom or Centerline is sufficient  
If a video is not found it will be skipped (maybe got deleted / expired).  
If a video is already downloaded (ie. already present in the ./media folder) it will be skipped  


### Command prompt examples:
- Download all videos, from all days  
    python download.py path_to_cookie_file 

- Download top and bottom perspectives from all days  
    python download.py path_to_cookie_file --perspective="bottom top"

- Download all perspectives from 29/12/2025 onwards   
    python download.py path_to_cookie_file --start="29/12/2025"

- Download all perspectives from 29/12/2025  
    python download.py path_to_cookie_file --start="29/12/2025" --oneday="y"


