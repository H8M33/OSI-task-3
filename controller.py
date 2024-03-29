import os
import signal
import sys

def handler(signum, frame):
    if signum == signal.SIGUSR1:
        global count
        print(f"Produced: {count}")
        sys.stderr.write(output)

pipe1 = os.pipe()
pipe0 = os.pipe()
pipe2 = os.pipe()

pid1 = os.fork()
if pid1 == 0:
    os.close(pipe1[0])
    os.dup2(pipe1[1], 1)
    os.execve('./producer.py', ['./producer.py'], os.environ)
else:
    pid2 = os.fork()
    if pid2 == 0:
        os.close(pipe0[1])
        os.dup2(pipe0[0], 0)
        os.close(pipe2[0])
        os.dup2(pipe2[1], 1)
        os.execve('/usr/bin/bc', ['/usr/bin/bc'], os.environ)
    else:
        os.close(pipe1[1])
        os.close(pipe0[0])
        os.close(pipe2[1])
        
        signal.signal(signal.SIGUSR1, handler)
        
        count = 0
        while True:
            line = os.read(pipe1[0], 100)
            if not line:
                break
            
            count += 1
            
            os.write(pipe0[1], line)
            
            result = os.read(pipe2[0], 100)
            
            expression = line.decode().strip()
            result = result.decode().strip()
            
            print(f"{expression} = {result}")
            
        print(f"Produced: {count}")
