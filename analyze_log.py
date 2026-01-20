
import re

log_path = 'backend/full_execution_log.txt'

target_lines = []
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        if "Tested ['ema_short', 'sma_medium', 'sma_long']" in line and "'ema_short': 3" in line:
            target_lines.append(line.strip())

print(f"Found {len(target_lines)} lines matching ema_short=3")
for line in target_lines[:5]:
    print(line)
