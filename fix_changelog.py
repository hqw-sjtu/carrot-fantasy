import re

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复版本号和时间
content = content.replace('## [1.6.8] - 2026-04-12 00:23', '## [1.6.9] - 2026-04-12 01:23')

with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("Fixed!")