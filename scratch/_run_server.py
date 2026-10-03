"""Launcher server utama yang aman untuk environment Python embedded
(sys.path tidak otomatis memuat folder project). Dipakai untuk testing;
start_server.bat tidak berubah."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import runpy

runpy.run_path(os.path.join(ROOT, 'server.py'), run_name='__main__')
