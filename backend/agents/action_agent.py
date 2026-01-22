import os
from datetime import datetime
from google import genai


class ActionAgent:
    """
    Action Agent:
    - Gemini used for educational explanations
    - Fully fault-tolerant (quota-safe)
    """

    def __init__(self):
        self.client = None
        self.model_name = "models/gemini-2.5-flash"

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print("Gemini client init failed:", e)

    def act(self, decision):
        disease = decision.get("Predicted Disease", "Unknown")
        confidence = decision.get("Confidence (%)", "N/A")
        severity = decision.get("Severity Level", "N/A")

        # Default fallback (ALWAYS works)
        explanation = (
            f"Possible Symptoms: Symptoms vary depending on severity of {disease}.\n"
            "Precautions: Avoid smoking, maintain hygiene, stay hydrated.\n"
            "Recommended Next Diagnostic Step: Consult a healthcare professional."
        )

        # Try Gemini (optional)
        if self.client:
            try:
                prompt = f"""
Provide GENERAL EDUCATIONAL information about {disease}.

Rules:
- No diagnosis
- No treatment or medication
- Simple language

Format:
Possible Symptoms:
Precautions:
Recommended Next Diagnostic Step:
"""
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )

                if response and response.text:
                    explanation = response.text.strip()

            except Exception as e:
                # Quota errors land here safely
                print("Gemini unavailable (quota or rate limit):", e)

        return {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Predicted Disease": disease,
            "Confidence": confidence,
            "Severity (AI-estimated)": severity,
            "Medical Guidance": explanation,
            "Disclaimer": (
                "This is an AI-assisted educational tool. "
                "It does not replace professional medical advice."
            )
        }
