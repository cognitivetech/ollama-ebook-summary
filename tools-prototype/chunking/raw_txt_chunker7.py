import sys
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models
from gensim.models.coherencemodel import CoherenceModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Preprocessing function
def preprocess(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]
    return tokens

# Segment text into chunks (e.g., sentences)
def segment_text(text):
    sentences = sent_tokenize(text)
    return sentences

# Function to compute coherence score
def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())
    return model_list, coherence_values

# Determine the optimal number of topics
def determine_optimal_num_topics(texts, limit=40, start=2, step=6):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    model_list, coherence_values = compute_coherence_values(dictionary, corpus, texts, limit, start, step)
    
    # Plot coherence values
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.xlabel("Number of Topics")
    plt.ylabel("Coherence Score")
    plt.title("Coherence Score vs. Number of Topics")
    plt.show()
    
    # Choose the model with the highest coherence score
    optimal_model = model_list[coherence_values.index(max(coherence_values))]
    num_topics = optimal_model.num_topics
    print(f"Optimal number of topics: {num_topics}")
    return num_topics

# Apply LDA to identify topics
def apply_lda(chunks, num_topics):
    processed_chunks = [preprocess(chunk) for chunk in chunks]
    dictionary = corpora.Dictionary(processed_chunks)
    corpus = [dictionary.doc2bow(chunk) for chunk in processed_chunks]
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    return lda_model, corpus, dictionary

# Convert topic distribution to fixed-size vector
def topic_distribution_to_vector(topic_distribution, num_topics):
    vector = np.zeros(num_topics)
    for topic, prob in topic_distribution:
        vector[topic] = prob
    return vector

# Calculate topic distributions
def get_topic_distributions(lda_model, corpus, num_topics):
    topic_distributions = [topic_distribution_to_vector(lda_model[doc], num_topics) for doc in corpus]
    return topic_distributions

# Identify topic shifts
def identify_topic_shifts(topic_distributions, threshold=0.6):
    boundaries = []
    for i in range(1, len(topic_distributions)):
        prev_dist = topic_distributions[i-1]
        curr_dist = topic_distributions[i]
        similarity = cosine_similarity([prev_dist], [curr_dist])[0][0]
        if similarity < threshold:
            boundaries.append(i)
    return boundaries

# Main function to chunk text
def chunk_text(text, threshold=0.6):
    chunks = segment_text(text)
    processed_chunks = [preprocess(chunk) for chunk in chunks]
    num_topics = determine_optimal_num_topics(processed_chunks)
    lda_model, corpus, dictionary = apply_lda(chunks, num_topics)
    topic_distributions = get_topic_distributions(lda_model, corpus, num_topics)
    boundaries = identify_topic_shifts(topic_distributions, threshold)
    return chunks, boundaries

# Function to read text file
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Function to write chunks to CSV
def write_chunks_to_csv(chunks, boundaries, output_file):
    chunked_texts = []
    start = 0
    for boundary in boundaries:
        chunk = ' '.join(chunks[start:boundary]).replace('\n', ' ')
        chunked_texts.append(chunk)
        start = boundary
    chunk = ' '.join(chunks[start:]).replace('\n', ' ')
    chunked_texts.append(chunk)
    
    df = pd.DataFrame({'Chunk': chunked_texts})
    df.to_csv(output_file, index=False)

# Main function to process file
def process_file(input_file):
    text = read_text_file(input_file)
    chunks, boundaries = chunk_text(text)
    output_file = os.path.splitext(input_file)[0] + '_chunked.csv'
    write_chunks_to_csv(chunks, boundaries, output_file)
    print(f"Chunks written to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = sys.argv[1]
    process_file(input_file)
