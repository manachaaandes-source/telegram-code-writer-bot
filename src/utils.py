from datetime import datetime

user_settings = {}  # {user_id: {"lang": "Python", "length": "medium"}}

def get_user_setting(user_id, key, default):
    return user_settings.get(user_id, {}).get(key, default)

def set_user_setting(user_id, key, value):
    user_settings.setdefault(user_id, {})[key] = value

def save_code_to_file(code):
    filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return filename
