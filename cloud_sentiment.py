from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def analyze_sentiment(text):
    client = language.LanguageServiceClient()
    type_ = enums.Document.Type.PLAIN_TEXT

    text_language = "en"
    document = {"content": text, "type": type_, "language": text_language}

    encoding_type = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_type)

    sentiment = response.document_sentiment
    sentiment_score = sentiment.score
    sentiment_magnitude = sentiment.magnitude

    # -1 means super sad
    # +1 means super happy

    # sentiment magnitude is strength of emotion
    print(sentiment_score)
    print(sentiment_magnitude)

    return sentiment_score, sentiment_magnitude
