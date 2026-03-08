import json
import os
from datetime import datetime

from google import genai


class ActionAgent:
    """
    Action Agent:
    - Generates user-friendly response
    - Adds Gemini explanation
    - Adds Gemini-based risk analysis with patient context
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

    def _default_risk_analysis(self, age, previous_disease, disease, confidence):
        risk_level = "Medium" if confidence >= 40 else "Low"
        if age >= 60 or previous_disease.strip():
            risk_level = "High" if confidence >= 60 else "Medium"

        age_impact = (
            "Age may increase vulnerability to respiratory complications."
            if age >= 60
            else "Age alone is not a major risk amplifier in this assessment."
        )

        previous_impact = (
            "Existing medical history may increase severity and recovery time."
            if previous_disease.strip()
            else "No previous disease history provided."
        )

        possible_contribution = (
            f"Previous condition ({previous_disease}) could contribute to the current lung condition."
            if previous_disease.strip()
            else "No direct previous-disease contribution identified from provided context."
        )

        recommendations = [
            "Consult a pulmonologist for clinical correlation.",
            "Repeat imaging or blood tests if symptoms worsen.",
            "Follow physician advice and avoid self-medication.",
        ]

        return {
            "Risk Level": risk_level,
            "Age Impact": age_impact,
            "Previous Disease Impact": previous_impact,
            "Possible Contribution": possible_contribution,
            "Recommendations": recommendations,
        }

    def _generate_risk_analysis(self, age, previous_disease, disease, confidence):
        fallback = self._default_risk_analysis(
            age=age,
            previous_disease=previous_disease,
            disease=disease,
            confidence=confidence,
        )

        if not self.client:
            return fallback

        try:
            prompt = f"""
You are a medical AI reasoning assistant for educational risk stratification.
Input:
- Age: {age}
- Previous disease: {previous_disease or "None"}
- Predicted lung disease: {disease}
- Model confidence percent: {confidence}

Return STRICT JSON only with this schema:
{{
  "Risk Level": "Low|Medium|High",
  "Age Impact": "text",
  "Previous Disease Impact": "text",
  "Possible Contribution": "text",
  "Recommendations": ["point1", "point2", "point3"]
}}
Keep language concise and clinically cautious. No markdown.
"""
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            text = (response.text or "").strip() if response else ""
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:].strip()

            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                return fallback

            if not isinstance(parsed.get("Recommendations"), list):
                parsed["Recommendations"] = fallback["Recommendations"]

            for key in [
                "Risk Level",
                "Age Impact",
                "Previous Disease Impact",
                "Possible Contribution",
            ]:
                if key not in parsed or not parsed[key]:
                    parsed[key] = fallback[key]

            if parsed["Risk Level"] not in {"Low", "Medium", "High"}:
                parsed["Risk Level"] = fallback["Risk Level"]

            return parsed

        except Exception as e:
            print("Gemini risk analysis unavailable:", e)
            return fallback

    def act(self, decision, patient_context=None):
        disease = decision.get("Predicted Disease", "Unknown")
        confidence = decision.get("Confidence (%)", "N/A")
        severity = decision.get("Severity Level", "N/A")
        heatmap = decision.get("heatmap")

        patient_context = patient_context or {}
        age = int(patient_context.get("age", 0))
        previous_disease = str(patient_context.get("previous_disease", "")).strip()

        explanation = (
            f"Possible Symptoms: Symptoms vary depending on severity of {disease}.\n"
            "Precautions: Avoid smoking, maintain hygiene, stay hydrated.\n"
            "Recommended Next Diagnostic Step: Consult a healthcare professional."
        )

        if self.client:
            try:
                prompt = f"""
Provide GENERAL EDUCATIONAL information about {disease}.
No diagnosis or treatment.
Simple language.

Format:
Possible Symptoms:
Precautions:
Recommended Next Diagnostic Step:
"""
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )

                if response and response.text:
                    explanation = response.text.strip()

            except Exception as e:
                print("Gemini guidance unavailable:", e)

        risk_analysis = self._generate_risk_analysis(
            age=age,
            previous_disease=previous_disease,
            disease=disease,
            confidence=float(confidence) if confidence != "N/A" else 0.0,
        )

        return {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Predicted Disease": disease,
            "Confidence": confidence,
            "Severity (AI-estimated)": severity,
            "Medical Guidance": explanation,
            "Risk Analysis": risk_analysis,
            "heatmap": heatmap,
            "Disclaimer": (
                "This is an AI-assisted educational tool. "
                "It does not replace professional medical advice."
            ),
        }
