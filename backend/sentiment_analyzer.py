from transformers import pipeline

class SentimentAnalyzer:
    
    def __init__(self):
        """
        Initializes the SentimentAnalyzer by loading the machine learning model.
        This is a one-time operation that happens when the server starts.
        """
        print("Loading sentiment analysis model...")
        
        # We use the 'pipeline' from the transformers library, which simplifies using
        # pre-trained models. 'distilbert-base-uncased-finetuned-sst-2-english' is a
        # popular choice because it's small, fast, and accurate for general sentiment.
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        print("Sentiment model loaded.")

    def analyze(self, text: str) -> str:
        """
        Analyzes a string of text and returns its sentiment.

        Args:
            text: The sentence or phrase to analyze.

        Returns:
            A string: 'Positive', 'Negative', or 'Neutral'.
        """
        try:
            # The pipeline returns a list of dictionaries. For a single sentence,
            # we just need the first result.
            # e.g., [{'label': 'POSITIVE', 'score': 0.9998}]
            results = self.sentiment_pipeline(text)
            
            label = results[0]['label']
            score = results[0]['score']

            # We use a high confidence threshold (0.85) to avoid mislabeling
            # neutral statements. Only strong sentiment is flagged.
            if label == 'POSITIVE' and score > 0.85:
                return 'Positive'
            if label == 'NEGATIVE' and score > 0.85:
                return 'Negative'
            
            # If the sentiment is not strong, or if it's mixed, we default to Neutral.
            return 'Neutral'
        except Exception as e:
            # If any error occurs during analysis, we default to Neutral to prevent crashes.
            print(f"Error during sentiment analysis: {e}")
            return "Neutral"

# Create a single, global instance of the service.
# This ensures the model is only loaded into memory once when the server starts.
sentiment_analyzer = SentimentAnalyzer()