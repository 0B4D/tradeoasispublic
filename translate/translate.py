from deep_translator import GoogleTranslator

def translate_to_croatian(text):
    translator = GoogleTranslator(source="en", target="hr")
    return translator.translate(text)

