from .key_ring import get_api_key
import deepl

class DeepLTranslator:
    def __init__(self):
        api_key = get_api_key("DeepL")
        self._cache = {}
        if not api_key:
            self.deepl_client = None
        else:
            self.deepl_client = deepl.DeepLClient(api_key)
        
    def translate(self, text: str, target_lang: str = "EN-US"):
        if not self.deepl_client:
            return text
        if text in self._cache:
            return self._cache[text]
        res = self.deepl_client.translate_text(text, target_lang=target_lang)
        self._cache[text] = res.text
        return res.text
    
    def translate_many(self, texts, target_lang: str = "EN-US"):
        to_send = [t for t in texts if t and t not in self._cache]
        if to_send:
            res = self.deepl_client.translate_text(to_send, target_lang=target_lang)
            for input, returned in zip(to_send, res):
                self._cache[input] = returned.text 
        return [self._cache.get(t, t) for t in texts]
            
