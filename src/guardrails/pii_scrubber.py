from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
import spacy

class PIIScrubber:
    def __init__(self):
        # Configure Presidio to use the lightweight en_core_web_sm model
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        
        # Set up the analyzer and anonymizer engines
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
        self.anonymizer = AnonymizerEngine()

    def scrub(self, text: str) -> str:
        """
        Detects and anonymizes PII in the given text.
        """
        # Analyze the text to identify PII entities
        results = self.analyzer.analyze(
            text=text,
            entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "US_SSN", "PERSON", "IBAN_CODE", "US_BANK_NUMBER"],
            language='en'
        )
        
        # Anonymize the findings
        anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
        
        return anonymized_result.text

# Example usage
if __name__ == "__main__":
    scrubber = PIIScrubber()
    sample_text = "Please contact John Doe at john.doe@example.com or call 555-123-4567. SSN is 000-00-0000."
    print("Original:", sample_text)
    print("Scrubbed:", scrubber.scrub(sample_text))
