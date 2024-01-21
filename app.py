from flask import Flask, request, render_template
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import urllib.parse
import os
import re
from googletrans import Translator
from itertools import combinations

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    hashtags = []
    search_links = {}
    temat = ''
    content_types = ['audio', 'images', 'videos', 'articles']  # Domyslnie wszystkie typy zawartosci sa zaznaczone

    if request.method == 'POST':
        temat = request.form['temat']
        translated_temat = translate_to_english(temat)
        content_types = request.form.getlist('content_type')  # Aktualizacja na podstawie zaznaczonych opcji
        hashtags = get_tags(translated_temat)

        for tag in hashtags:
            instagram_tag = re.sub(r'[^\w]', '', tag)
            instagram_encoded_tag = urllib.parse.quote_plus(instagram_tag)
            general_encoded_tag = urllib.parse.quote_plus(tag)

            search_links[tag] = {
                'instagram': f'https://www.instagram.com/explore/tags/{instagram_encoded_tag}/' if 'images' in content_types or 'videos' in content_types else None,
                'youtube': f'https://www.youtube.com/results?search_query={general_encoded_tag}' if 'videos' in content_types else None,
                'soundcloud': f'https://soundcloud.com/search?q={general_encoded_tag}' if 'audio' in content_types else None,
                'spotify': f'https://open.spotify.com/search/{general_encoded_tag}' if 'audio' in content_types else None,
                'google_scholar': f'https://scholar.google.com/scholar?q={general_encoded_tag}' if 'articles' in content_types else None,
            }

    return render_template('index.html', hashtags=' '.join(hashtags), search_links=search_links, temat=temat, content_types=content_types)

def detect_language(text):
    translator = Translator()
    detected_language = translator.detect(text).lang
    return detected_language

def translate_to_english(text):
    detected_language = detect_language(text)
    if detected_language != 'en':
        translator = Translator()
        translated = translator.translate(text, src=detected_language, dest='en')
        return translated.text
    else:
        return text

def get_tags(translated_text):
    stop_words_set = set(stopwords.words('english'))
    words = word_tokenize(translated_text, language='english')
    words = [word for word in words if word not in string.punctuation]
    filtered_words = [word for word in words if word.lower() not in stop_words_set]
    compound_hashtags = generate_compound_hashtags(filtered_words)
    return compound_hashtags

def generate_compound_hashtags(words):
    compound_hashtags_2 = [' '.join(combo) for combo in combinations(words, 2)]
    compound_hashtags_3 = [' '.join(combo) for combo in combinations(words, 3)]
    compound_hashtags_4 = [' '.join(combo) for combo in combinations(words, 4)]
    return compound_hashtags_2 + compound_hashtags_3 + compound_hashtags_4

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))