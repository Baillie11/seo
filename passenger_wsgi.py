import os
import sys

# Add your application directory to Python path
INTERP = "/home/ozbizfin/virtualenv/icenspice.com/clickseo/3.9/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.path.dirname(__file__))

from app import app as application 