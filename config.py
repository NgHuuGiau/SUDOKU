"""Cau hinh chung cho game.
Chua bien ngon ngu hien tai va ham chuyen doi ngon ngu.
"""

ngon_ngu_hien_tai = "vi"


def chuyen_ngon_ngu():
    global ngon_ngu_hien_tai
    ngon_ngu_hien_tai = "vi" if ngon_ngu_hien_tai == "en" else "en"
