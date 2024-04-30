import os
import sys
import random
import string

numUsers=int(sys.argv[1])
for i in range(numUsers):
        chars = string.ascii_letters + string.digits
        random.seed = os.urandom(1024)
        password = ''.join(random.choice(chars) for c in range(10))
        os.system("./mkusr.sh "+str(i)+" "+password)


