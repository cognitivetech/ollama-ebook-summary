import argparse
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

class LongDocumentProcessor:
    def __init__(self, model_name='bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)
        self.max_length = 510  # Adjust based on the model's max input size

    def preprocess_text(self, raw_text):
        # Tokenize the document into sentences
        sentences = sent_tokenize(raw_text)
        return sentences

    def segment_document(self, sentences):
        # Segment the document into chunks that fit the model's input size
        segments = []
        current_segment = []
        current_length = 0
        for sentence in sentences:
            tokens = self.tokenizer.tokenize(sentence)
            # Check if adding the next sentence exceeds the max_length
            if current_length + len(tokens) > self.max_length:
                segments.append(current_segment)
                current_segment = []
                current_length = 0
            current_segment.extend(tokens)
            current_length += len(tokens)
        # Add the last segment if it's not empty
        if current_segment:
            segments.append(current_segment)
        return segments

    def classify_segments(self, segments):
        # Classify each segment and collect predictions
        predictions = []
        for segment in segments:
            inputs = self.tokenizer.encode_plus(segment, add_special_tokens=True, return_tensors='pt', truncation=True, max_length=self.max_length)
            with torch.no_grad():
                outputs = self.model(**inputs)
                prediction = softmax(outputs.logits, dim=1)
                predictions.append(prediction)
        return predictions

    def aggregate_predictions(self, predictions):
        # Aggregate predictions from all segments
        aggregated_prediction = torch.mean(torch.stack(predictions), dim=0)
        final_prediction = torch.argmax(aggregated_prediction).item()
        return final_prediction

    def process_document(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_text = file.read()
        sentences = self.preprocess_text(raw_text)
        segments = self.segment_document(sentences)
        predictions = self.classify_segments(segments)
        final_prediction = self.aggregate_predictions(predictions)
        return final_prediction

# Parse command line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a long document for classification.')
    parser.add_argument('file_path', type=str, help='Path to the text file to be processed.')
    args = parser.parse_args()

    processor = LongDocumentProcessor(model_name='bert-base-uncased')
    final_prediction = processor.process_document(args.file_path)
    print(f"Final Document Classification: {final_prediction}")
