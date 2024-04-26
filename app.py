# Importing necessary libraries
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import bs4 as bs
from bs4 import BeautifulSoup
import urllib.request
import re
import requests
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import heapq
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
import tempfile
import warnings

# Download NLTK resources if not already downloaded
import nltk
nltk.download('punkt')
nltk.download('stopwords')
warnings.filterwarnings("ignore")

# Initialize Flask app
app = Flask(__name__, template_folder='views')

# Function to remove special substrings from text
def remove_special_substrings(text):
    # Remove text inside slashes followed by capital letters
    text = re.sub(r'\/[A-Z][^\.!?]*[\.!?]', ' ', text)
    # Remove non-ASCII Unicode characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

# Function to generate summary of a YouTube video
def generate_video_summary(video_id):
    try:
        # Get transcript of the YouTube video
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        doc = " ".join([line['text'] for line in transcript])

        # Remove special substrings from the transcript
        doc = remove_special_substrings(doc)

        # Tokenize the transcript into words and sentences
        stops = set(stopwords.words('english'))
        word_array = word_tokenize(doc)

        # Calculate word frequency
        wordfreq = {}
        for word in word_array:
            word = word.lower()
            if word in stops:
                continue
            elif word in wordfreq:
                wordfreq[word] += 1
            else:
                wordfreq[word] = 1

        # Tokenize transcript into sentences
        sent_array = sent_tokenize(doc)

        # Calculate sentence frequency
        sentfreq = {}
        for sentence in sent_array:
            for word, freq in wordfreq.items():
                if word in sentence.lower():
                    if sentence in sentfreq:
                        sentfreq[sentence] += freq
                    else:
                        sentfreq[sentence] = freq

        # Calculate average sentence frequency
        averageval = 0
        for sentence in sentfreq:
            averageval += sentfreq[sentence]

        average = int(averageval / len(sentfreq))

        # Generate summary based on sentence frequency
        summary = ''
        for sentence in sent_array:
            if (sentence in sentfreq) and (sentfreq[sentence] > (1.5 * average)):
                summary = summary + " " + sentence

        return summary
    except Exception as e:
        print("An error occurred while generating video summary:", e)
        return "Error Occurred. Please try another URL!"

# Function to extract text and headings from a given URL
def get_text_and_headings_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract text from paragraphs
    paragraphs = soup.find_all('p')
    text = [p.text.strip() for p in paragraphs]
    
    # Extract headings from h1, h2, h3, etc. tags
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    heading_text = [heading.text.strip() for heading in headings]
    
    return text, heading_text

# Function to summarize a paragraph
def summarize_paragraph(paragraph):
    # Tokenize sentences
    sentences = sent_tokenize(paragraph)
    
    # Tokenize words and remove stopwords
    stopwords1 = set(stopwords.words("english"))
    word_frequencies = {}
    for sentence in sentences:
        for word in sentence.lower().split():
            if word not in stopwords1:
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    
    # Calculate weighted frequencies of sentences
    maximum_frequency = max(word_frequencies.values(), default=1)
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        score = sum(word_frequencies.get(word, 0) for word in sentence.lower().split())
        sentence_scores[sentence] = score
    
    # Get the top sentence
    if sentence_scores:
        summary_sentence = max(sentence_scores, key=sentence_scores.get)
    else:
        summary_sentence = "No content"
    
    return summary_sentence

# Function to summarize text with headings
def summarize_with_headings(text, headings):
    summary = {}
    for idx, paragraph in enumerate(text):
        paragraph_summary = summarize_paragraph(paragraph)
        if idx < len(headings):
            heading = headings[idx]
        else:
            heading = f"Paragraph {idx+1}"
        summary[heading.strip('"')] = paragraph_summary.strip('"')
    
    return summary

# Function to process audio file and generate summary
def process_audio(filename):
    try:
        summary = ""
        audio = AudioSegment.from_wav(filename)
        chunks = make_chunks(audio, 8000)

        recognizer = sr.Recognizer()
        for i, chunk in enumerate(chunks):
            print("Processing chunk", i)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                chunk.export(temp_wav.name, format="wav")
                with sr.AudioFile(temp_wav.name) as source:
                    audio_data = recognizer.record(source)
                    try:
                        rec = recognizer.recognize_google(audio_data)
                        summary += rec + ". "
                    except sr.UnknownValueError:
                        print("Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
            os.unlink(temp_wav.name)  # Delete the temporary WAV file after processing
        return summary
    except Exception as e:
        print("An error occurred while processing audio:", e)
        return "Error Occurred. Please try another audio file."

# Route for the homepage
@app.route('/')
def index():
    return render_template('createsummary.ejs')

# Route to process video
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        video_link = data['video_link']
        video_id = video_link.split("=")[1]
        summary = generate_video_summary(video_id)
        if summary=="":
            return "Error Occurred. Please try another video url.", 500
        return jsonify(summary)
    except Exception as e:
        print("An error occurred:", e)
        return "Error Occurred. Please try another URL!", 500

# Route to process text from a URL
@app.route('/process_text', methods=['POST'])
def get_text_and_headings():
    try:
        data = request.get_json()
        url = data['url']
        text, headings = get_text_and_headings_from_url(url)
        summary = summarize_with_headings(text, headings)
        return jsonify(summary)
    except Exception as e:
        print("An error occurred:", e)
        return "Error Occurred. Please try another URL!", 500

# Route to process audio file
@app.route('/process_audio', methods=['POST'])
def process_audio_route():
    try:
        file = request.files['audio_file']
        filename = os.path.join(tempfile.gettempdir(), 'temp.wav')
        file.save(filename)
        summary = process_audio(filename)
        if summary == "":
            return "Error Occurred. Please try another audio file.", 500
        else:
            return jsonify({"summary": summary})  # Return the summary as JSON
    except Exception as e:
        print("An error occurred:", e)
        return "Error Occurred. Please try another audio file.", 500

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
