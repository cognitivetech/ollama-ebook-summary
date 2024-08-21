class ChunkerBase:
    id = "00"  # Default ID, override in child classes

    def preprocess_text(self, text):
        raise NotImplementedError

    def chunk_text(self, text):
        raise NotImplementedError
