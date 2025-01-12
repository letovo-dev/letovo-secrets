import os
import subprocess


def get_ip():
    try:
        return os.getenv('CURRENT_IP')
    except:
        return "91.203.232.173"