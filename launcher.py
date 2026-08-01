# launcher.py
import subprocess
import os
import sys
import time

def find_project_dir():
    """Ищет папку проекта — там же где лежит лаунчер."""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    if os.path.exists(os.path.join(exe_dir, 'app.py')):
        return exe_dir
    
    return None


def kill_app():
    """Убивает процесс app.py по PID из файла и чистит порт."""
    pid_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.pid')
    
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            subprocess.run(f'taskkill /f /pid {pid}', shell=True, capture_output=True)
            print(f"Процесс app.py (PID {pid}) остановлен.")
        except:
            pass
        try:
            os.remove(pid_file)
        except:
            pass
    
    # Чистим порт 5000
    result = subprocess.run(
        'netstat -ano | findstr :5000 | findstr LISTENING',
        shell=True, capture_output=True, text=True
    )
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                try:
                    subprocess.run(f'taskkill /f /pid {pid}', shell=True, capture_output=True)
                except:
                    pass
    
    for _ in range(10):
        check = subprocess.run(
            'netstat -ano | findstr :5000 | findstr LISTENING',
            shell=True, capture_output=True, text=True
        )
        if not check.stdout:
            break
        time.sleep(1)
    time.sleep(1)


def main():
    project_dir = find_project_dir()
    
    if not project_dir:
        print("Ошибка: app.py не найден рядом с лаунчером")
        input("Нажмите Enter для выхода...")
        return
    
    os.chdir(project_dir)
    
    venv_python = os.path.join(project_dir, 'venv', 'Scripts', 'python.exe')
    if not os.path.exists(venv_python):
        venv_python = 'python'
    
    print(f"Папка проекта: {project_dir}")
    print(f"Python: {venv_python}")
    print("DayZ Manager запущен.")
    print("Ctrl+C — остановка")
    print("=" * 50)
    
    kill_app()
    
    process = subprocess.Popen(
        [venv_python, 'app.py'],
        cwd=project_dir,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    pid_file = os.path.join(project_dir, 'app.pid')
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))
    
    print(f"app.py запущен (PID: {process.pid})")
    print("=" * 50)
    
    try:
        while True:
            if process.poll() is not None:
                exit_code = process.returncode
                print(f"\napp.py остановлен (код: {exit_code}). Перезапуск через 3 секунды...")
                time.sleep(3)
                kill_app()
                process = subprocess.Popen(
                    [venv_python, 'app.py'],
                    cwd=project_dir,
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
                print(f"app.py перезапущен (PID: {process.pid})")
                print("=" * 50)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка менеджера...")
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except:
                process.kill()
        kill_app()
        print("Менеджер остановлен.")


if __name__ == '__main__':
    main()