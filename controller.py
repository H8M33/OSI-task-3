import os
import signal
import subprocess

def handler(signum, frame):
    if signum == signal.SIGUSR1:
        print(f"Produced: {count}")

pipe1 = os.pipe()
pipe0 = os.pipe()
pipe2 = os.pipe()

pid1 = os.fork()
if pid1 == 0:
    os.close(pipe1[0])
    os.dup2(pipe1[1], 1)
    os.execlp("python", "python", "producer.py")
else:
    pid2 = os.fork()
    if pid2 == 0:
        os.close(pipe0[1])
        os.dup2(pipe0[0], 0)
        os.close(pipe2[0])
        os.dup2(pipe2[1], 1)
        os.execlp("/usr/bin/bc", "bc")
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
