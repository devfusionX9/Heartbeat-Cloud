import psutil

WATCH_PROCESSES = ["your_process_1.py", "your_process_2.py"]

def get_process_report():
    found = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent']):
        try:
            cmd = " ".join(proc.info['cmdline'])
            for name in WATCH_PROCESSES:
                if name in cmd:
                    found.append(
                        f"{name} | PID={proc.info['pid']} | CPU={proc.cpu_percent()}%"
                    )
        except:
            pass

    if not found:
        return "⚙️ ПРОЦЕССЫ НЕ НАЙДЕНЫ"

    return "⚙️ ПРОЦЕССЫ:\n\n" + "\n".join(found)
