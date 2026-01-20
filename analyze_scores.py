
import re

log_path = 'backend/full_execution_log.txt'

# Find the start of the last session
last_session_start = 0
current_line = 0

lines = []
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look for "BacktestService initialized" or similar start marker backwards
for i in range(len(lines) - 1, -1, -1):
    if "BacktestService initialized" in lines[i]:
        last_session_start = i
        break

print(f"Analyzing session starting at line {last_session_start}")

session_lines = lines[last_session_start:]
ema3_scores = []
ema13_scores = []
best_score = -1.0
best_config = None

for line in session_lines:
    if "Tested ['ema_short'" in line:
        # Extract Score
        score_match = re.search(r"Score: ([\d\.]+)", line)
        if score_match:
            score = float(score_match.group(1))
            
            if score > best_score:
                best_score = score
                best_config = line.strip()

            if "'ema_short': 3," in line:
                ema3_scores.append(score)
            elif "'ema_short': 13," in line:
                ema13_scores.append(score)

print(f"Found {len(ema3_scores)} tests for EMA 3. Max Score: {max(ema3_scores) if ema3_scores else 0}")
print(f"Found {len(ema13_scores)} tests for EMA 13. Max Score: {max(ema13_scores) if ema13_scores else 0}")

print(f"\nOverall Best Score in logs: {best_score}")
print(f"Best Config Log: {best_config}")
