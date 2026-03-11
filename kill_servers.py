import os
import subprocess

ports = [8000, 5173, 8501]
try:
    for port in ports:
        try:
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            for line in output.strip().split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    try:
                        subprocess.call(['taskkill', '/F', '/PID', pid], shell=True)
                        print(f"Killed process {pid} on port {port}")
                    except Exception as inner_e:
                        print(f"Failed to kill {pid}: {inner_e}")
        except subprocess.CalledProcessError:
            print(f"No process listening on port {port}")
except Exception as e:
    print(f"Error: {e}")
