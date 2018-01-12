import sys
from datetime import datetime
try:
    print("Hello World")
    difftime=int(sys.argv[1])
    print("difference of time %s"%difftime)
    if difftime < 1:
        raise Exception('spam', 'eggs')
except:
    print datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Unexpected error:%s"%sys.exc_info()[0]
    sys.exit(1)
