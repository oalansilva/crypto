import os
import re

def remove_emojis(text):
    # Basic regex for emojis (surrogates and other ranges)
    # This is a simplified regex, but should catch most common emojis used in logs: 🔍, ✅, ❌, 📅, 📦, 👉, 🔒, 💾, 📊, 🏆, 🔄
    # Range: U+1F300-U+1F9FF (Misc Symbols and Pictographs, Emoticons, Transport, etc)
    # Also U+2700-U+27BF (Dingbats like ✅)
    return re.sub(r'[\U0001f300-\U0001f9ff\u2700-\u27bf]', '', text)

root_dir = 'backend'

print("Cleaning emojis from python files...")

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.py'):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = remove_emojis(content)
                
                if new_content != content:
                    print(f"fixing {filepath}")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

print("Done.")
