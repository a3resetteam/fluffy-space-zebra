# Fix the corrupted BASE_TEMPLATE section
python3 -c "
import re
with open('app_fixed.py', 'r') as f:
    content = f.read()

# Find and replace the corrupted BASE_TEMPLATE
fixed_template = '''# Templates
BASE_TEMPLATE = \'\'\'
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>MYA3Reset: The Oracle</title>
    <style>
        body {
            font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #000000;
            min-height: 100vh;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: #000000; border: 2px solid #333333; border-radius: 20px; padding: 40px; margin-bottom: 30px; }
        .form-group { margin-bottom: 25px; }
        .form-group input { width: 100%; padding: 15px; border: 2px solid #333; border-radius: 12px; background: #000000; color: #ffffff; }
        .btn { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: #ffffff; padding: 15px 35px; border: none; border-radius: 12px; text-decoration: none; display: inline-block; margin: 8px; }
        .modes-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin-top: 40px; }
        .mode-card { background: #000000; border: 2px solid #333; border-radius: 20px; padding: 35px; text-align: center; }
    </style>
</head>
<body>
    <div class=\"container\">{{ content }}</div>
</body>
</html>
\'\'\'\'

# Replace the corrupted section
start_pattern = r'<meta name=\"viewport\".*?padding: 40px;'
content = re.sub(start_pattern, fixed_template, content, flags=re.DOTALL)

with open('app_fixed.py', 'w') as f:
    f.write(content)
"
