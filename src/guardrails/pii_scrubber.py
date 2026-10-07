from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIScrubber:
    def __init__(self):
        # Set up the analyzer and anonymizer engines
        self.analyzer = AnalyzerEngine()
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
