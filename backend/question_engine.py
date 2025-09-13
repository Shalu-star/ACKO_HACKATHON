import re
from typing import List, Dict

class QuestionEngine:
    def __init__(self):
        # Inline full ACKO script (condensed per module)
        self.script_rules = {
            "basic_information": {
                "questions": [
                    "Could you please confirm your full name?",
                    "Could you please confirm your date of birth?",
                    "Please provide the height and weight details for all members to be covered."
                ]
            },
            "lifestyle": {
                "questions": [
                    "Has anyone used tobacco products in the past year?",
                    "How frequently? (Daily / Weekly / Few times a year)",
                    "Has anyone consumed alcohol in the past year?",
                    "How frequently? (Daily / Weekly / Few times a year)"
                ]
            },
            "medical_history": {
                "questions": [
                    "Has anyone been diagnosed with any of the following conditions: Diabetes, High blood pressure, Thyroid disorder, Asthma, Cataract, Glaucoma, Arthritis, Spondylosis, Hernia, Kidney disorders, Liver disorders, Heart disease, Stroke, Epilepsy, Cancer, Mental health conditions, Anemia, Sleep apnea, Piles, Autoimmune disorders, or others?",
                    "When was it diagnosed?",
                    "What treatment was given - medical, surgical, or hospitalization?",
                    "Are any medications being taken? Please specify names and dosages.",
                    "Were there any surgical procedures or hospitalizations? Please provide the year and details.",
                    "Are there any ongoing symptoms?",
                    "Have there been any recurrences or complications?",
                    "Have there been any relevant investigations in the last 3 months?",
                    "Could you share your treating doctor's name and clinic/hospital details?"
                ]
            },
            "recent_health_status": {
                "questions": [
                    "Have any members taken prescribed medicines in the past few weeks?",
                    "Is anyone currently experiencing any of these symptoms: pain, fatigue, weight loss, dizziness, breathing difficulty, acidity, bleeding, vision issues, ENT issues, swelling, numbness, difficulty walking?"
                ]
            },
            "hospitalization": {
                "questions": [
                    "Has anyone been advised to undergo or has undergone hospitalization for any illness or surgery?",
                    "What was the surgery for and when was it performed?",
                    "How many days was the hospitalization?",
                    "Were there any post-surgery complications?",
                    "Are there any current symptoms or recurrence?"
                ]
            },
            "female_health": {
                "questions": [
                    "Is anyone currently pregnant?",
                    "When is the baby due? (1-3, 3-6, or 6-9 months)",
                    "Are there any pregnancy-related complications?",
                    "Are there any pregnancy-related medications being taken?",
                    "Has anyone experienced gynecological issues like menstrual complaints, breast lumps, fibroid uterus, or endometriosis?"
                ]
            },
            "insurance_history": {
                "questions": [
                    "Do you have any existing health insurance coverage?",
                    "Have you made any claims in the last 5 years?",
                    "Has any health insurance proposal ever been declined, postponed, or accepted with special terms?"
                ]
            },
            "final_confirmation": {
                "questions": [
                    "Is there anything else about your health you'd like to share?",
                    "Please confirm that you've provided accurate information to the best of your knowledge."
                ]
            }
        }

        # Track which modules we’ve already covered
        self.already_covered = set()

        # Build keyword map for reflexive matching
        self.keyword_map = self._build_keyword_index()

    def _build_keyword_index(self) -> Dict[str, str]:
        keyword_map = {}
        for module, content in self.script_rules.items():
            for q in content.get("questions", []):
                for word in re.findall(r"\b[a-zA-Z]{4,}\b", q.lower()):
                    if word not in keyword_map:
                        keyword_map[word] = module
        return keyword_map

    def detect_sentiment(self, text: str) -> str:
        distress_words = ["confused", "worried", "scared", "anxious", "don't know"]
        if any(w in text for w in distress_words):
            return "distress"
        return "neutral"

    async def generate_question(
        self,
        conversation_history: List[Dict],
        checklist_step: str
    ) -> List[Dict]:
        last_patient_response = ""
        for entry in reversed(conversation_history):
            if entry.get("speaker") == "Patient":
                last_patient_response = entry.get("text", "").lower()
                break

        if not last_patient_response:
            return []

        sentiment_flag = self.detect_sentiment(last_patient_response)

        # Look for keywords in the last patient response
        for word in re.findall(r"\b[a-zA-Z]{4,}\b", last_patient_response):
            if word in self.keyword_map:
                module = self.keyword_map[word]
                if module not in self.already_covered:
                    self.already_covered.add(module)
                    return [
                        {"question": q, "module": module, "sentiment": sentiment_flag}
                        for q in self.script_rules[module]["questions"]
                    ]
        return []

    def reset_session(self):
        self.already_covered.clear()


# Global instance
question_engine = QuestionEngine()