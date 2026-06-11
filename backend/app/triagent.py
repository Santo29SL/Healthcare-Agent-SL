
HIGH_RISK = set(
    ("chest pain",
    "difficulty breathing",
    "unconscious",
    "seizure",
    "heavy bleeding",
    "suicidal thoughts",
    "stroke symptoms")
)

NEGATIONS = {"no", "not", "dont", "don't", "without"}
emergency_symptoms = {'high' , 'severe', 'sudden', 'unbearable', 'worsening', 'persistent'}
def check_risk(user_query: str) -> dict:
    user_query = user_query.lower()

    for symptom in HIGH_RISK:
        symptom1 = "".join(symptom.split())

        if symptom in user_query or symptom1 in user_query:
            
            words = user_query.split()
            if symptom1 in user_query:
                symptom = symptom1
            symptom_words = symptom.split() #Check for simple negation

            for i in range(len(words) - len(symptom_words) + 1):
                if words[i:i+len(symptom_words)] == symptom_words:
                    
                    window = words[max(0, i-3):i] ## check previous 3 words for negation
                    if any(neg in window for neg in NEGATIONS):
                        continue

                    intensity_window = (
                        words[max(0, i-3):i] +
                        words[i+len(symptom_words): i+len(symptom_words)+3]
                    )
                    if any(emergency in emergency_symptoms for emergency in intensity_window):
                        return {
                        "risk_level": "moderate - high",
                        "advice": "Seek immediate medical attention or call emergency services."
                        }
                    return {
                        "risk_level": "high",
                        "advice": "Seek immediate medical attention or call emergency services."
                    }

    return {
        "risk_level": "low",
        "advice": "Monitor your symptoms and consult a healthcare professional if they worsen."
    }


# user_query = "I have no chest pain but high difficulty breathing."
# result = check_risk(user_query)