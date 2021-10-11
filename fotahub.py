import sys
if sys.version_info[0] < 3:
    print('ERROR: This program requires Python 3')
    sys.exit(1)

import fotahubclient.cli.main as fotahub

fotahub.main()