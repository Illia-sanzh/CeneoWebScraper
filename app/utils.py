from deep_translator import GoogleTranslator
import os

def extract_data(ancestor, selector=None, attribute=None, multiple=False):
    if selector:        
        if multiple:
            if attribute:
                return [tag[attribute].strip() for tag in ancestor.select(selector)]
            return [tag.text.strip() for tag in ancestor.select(selector)]
        if attribute:
            try:
                return ancestor.select_one(selector)[attribute].strip()
            except TypeError:
                return None
        try:
            return ancestor.select_one(selector).text.strip()
        except AttributeError:
            return None
    if attribute:
        return ancestor[attribute]
    return None
    
def translate_data(text, source='pl', target='en'):
    return GoogleTranslator(source, target).translate(text=text)

def make_dir_if_not(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
