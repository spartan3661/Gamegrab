import keyring
import keyring.errors
SERVICE_NAME = "OCRApp"

USERNAMES = {
    "DeepL": "deepl_api_key",
    "Azure": "azure_translator_key",
    "Google": "google_translate_key"
}

def set_api_key(provider: str, key: str):
    if provider not in USERNAMES:
        raise ValueError(f"Unknown provider: {provider}")
    keyring.set_password(SERVICE_NAME, USERNAMES[provider], key)

def get_api_key(provider: str):
    if provider not in USERNAMES:
        return None
    return keyring.get_password(SERVICE_NAME, USERNAMES[provider])

def delete_api_key(provider: str):
    if provider not in USERNAMES:
        return
    try:
        keyring.delete_password(SERVICE_NAME, USERNAMES[provider])
    except keyring.errors.PasswordDeleteError:
        pass
