from .key_ring import get_api_key
import deepl

class DeepLTranslator:
    def __init__(self):
        api_key = get_api_key("DeepL")
        if not api_key:
            self.deepl_client = None
        else:
            self.deepl_client = deepl.DeepLClient(api_key)
        
    def translate(self, text: str, target_lang: str = "EN-US"):
        if not self.deepl_client:
            return text
        res = self.deepl_client.translate_text(text, target_lang=target_lang)
        return res.text