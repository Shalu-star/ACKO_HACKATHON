from typing import List, Dict

class QuestionEngine:
    """
    The "brain" of the AI assistant. This version is a high-speed, rule-based
    engine that generates reflexive questions based on the ACKO consultation script.
    It uses a comprehensive dictionary to map patient-mentioned keywords to the
    exact follow-up questions required by the underwriting process.
    This implementation has NO external AI/LLM dependencies, making it
    extremely fast and reliable.
    """
    def __init__(self):
        """Initializes the Question Engine with the predefined ACKO script rules."""
        
        # This comprehensive dictionary is the core of our rule-based engine.
        # It maps keywords that a patient might say to a list of mandatory
        # follow-up questions from the hackathon problem statement.
        self.acko_script_rules = {
            # Medical History Module Keywords
            "diabetes": [
                "When was it diagnosed?",
                "What treatment was given - medical, surgical, or hospitalization?",
                "Are any medications being taken? If yes, please specify names and dosages."
            ],
            "blood pressure": [
                "When was it diagnosed?",
                "What are your typical blood pressure readings?",
                "Are any medications being taken? If yes, please specify names and dosages."
            ],
            "hypothyroid": ["When was it diagnosed?", "Are you taking any medication for it?"],
            "hyperthyroid": ["When was it diagnosed?", "Are you taking any medication for it?"],
            "thyroid": ["When was the thyroid condition diagnosed?", "What is your current medication dosage?"],
            "asthma": [
                "When was it diagnosed?",
                "How often do you use an inhaler?",
                "Have you ever been hospitalized for asthma?"
            ],
            "arthritis": [
                "When was it diagnosed?",
                "Which joints are affected?",
                "How does it impact your daily activities?"
            ],
            "surgery": [
                "What was the surgery for and when was it performed?",
                "Were there any post-surgery complications?",
                "Are there any current symptoms or recurrence?"
            ],
            "hospitalization": [
                "What was the reason for the hospitalization?",
                "What year was the hospitalization/surgery?",
                "How many days was the hospitalization?"
            ],
            "tobacco": ["How frequently do you use tobacco? Daily, weekly, or a few times a year?"],
            "alcohol": ["How frequently do you consume alcohol? Daily, weekly, or a few times a year?"],
            "pregnant": [
                "When is the baby due?",
                "Are there any pregnancy-related complications?",
                "Are there any pregnancy-related medications being taken?"
            ],
            # Add more specific keywords from the list for better coverage
            "cataract": ["When was the cataract diagnosed or operated on?", "Are there any ongoing vision issues?"],
            "glaucoma": ["When was glaucoma diagnosed?", "What treatment are you receiving?"],
            "hernia": ["When was the hernia diagnosed or operated on?", "Are there any current symptoms?"],
            "kidney": ["What is the specific kidney disorder?", "When was it diagnosed and what treatment was given?"],
            "liver": ["What is the specific liver disorder?", "When was it diagnosed and what treatment was given?"],
            "heart": ["What is the specific heart disease?", "Are you taking any medications for it?"],
            "cancer": ["What type of cancer or tumor was it?", "What was the treatment and when was it completed?"]
        }

    async def generate_question(self, conversation_history: List[Dict], checklist_step: str) -> List[str]:
        """
        Generates the next suggested question(s) for the doctor based on keyword matching.
        
        Args:
            conversation_history: The transcript of the conversation so far.
            checklist_step: The current step in the consultation checklist.

        Returns:
            A list of suggested questions, or an empty list if no keyword is matched.
        """
        last_patient_response = ""
        # Find the most recent thing the patient said.
        for entry in reversed(conversation_history):
            if entry.get("speaker") == "Patient":
                last_patient_response = entry.get("text", "").lower()
                break
        
        if not last_patient_response:
            return []

        # Iterate through our rulebook to find a matching keyword.
        for keyword, questions in self.acko_script_rules.items():
            if keyword in last_patient_response:
                # If a keyword is found, return the associated follow-up questions immediately.
                return questions
        
        # If no specific keywords are found in the patient's response,
        # return an empty list. The doctor can then proceed with the standard script.
        return []

# Create a single, global instance of the engine to be used by the main app.
question_engine = QuestionEngine()
