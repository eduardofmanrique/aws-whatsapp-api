import base64

def is_base64(string):
    try:
        # Attempt to decode the string using Base64
        decoded = base64.b64decode(string, validate=True)
        # Re-encode and compare to handle padding and character constraints
        return base64.b64encode(decoded).decode('utf-8') == string.strip()
    except Exception:
        return False