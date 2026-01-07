import re

# Read the file
with open('backend/app/services/sequential_optimizer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the duplicate function definition (lines 163-172)
# The pattern matches the first empty function definition
pattern = r'    def get_full_history_dates\(self, symbol: str\) -> Tuple\[str, str\]:\r?\n        """\r?\n        Auto-detect full available history for a symbol\.\r?\n        \r?\n        Args:\r?\n            symbol: Trading symbol\r?\n            \r?\n        Returns:\r?\n            Tuple of \(start_date, end_date\) as ISO strings\r?\n        """\r?\n    '

# Replace with empty string (remove it)
content = re.sub(pattern, '    ', content, count=1)

# Add logging line before return statement in the remaining function
content = content.replace(
    '        return start_date, end_date',
    '        print(f"📅 Full history period: {start_date} to {end_date} ({len(df)} candles)")\n        \n        return start_date, end_date'
)

# Write back
with open('backend/app/services/sequential_optimizer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed duplicate function and added logging")
