import numpy as np

class DecisionAgent:
    """
    Decision Agent:
    - Interprets CNN prediction probabilities
    - Applies confidence-based medical reasoning
    - Determines disease, severity, and reliability
    """

    def __init__(self):
        # Confidence thresholds (clinically inspired)
        self.high_confidence = 0.70
        self.medium_confidence = 0.40

    def decide(self, predictions):
        """
        Input  : Dictionary of class probabilities
        Output : Final medical decision with severity
        """

        # ----------------------------
        # 1. BEST CLASS SELECTION
        # ----------------------------
        disease = max(predictions, key=predictions.get)
        confidence = float(predictions[disease])

        # ----------------------------
        # 2. SEVERITY ASSESSMENT
        # ----------------------------
        if confidence >= self.high_confidence:
            severity = "High"
            recommendation = "Immediate clinical attention recommended."
        elif confidence >= self.medium_confidence:
            severity = "Medium"
            recommendation = "Further diagnostic tests advised."
        else:
            severity = "Low"
            recommendation = "Monitoring suggested; low confidence diagnosis."

        # ----------------------------
        # 3. RELIABILITY CHECK
        # ----------------------------
        reliable = confidence >= self.medium_confidence

        # ----------------------------
        # 4. FORMAT RESPONSE
        # ----------------------------
        return {
            "Predicted Disease": disease,
            "Confidence (%)": round(confidence * 100, 2),
            "Severity Level": severity,
            "Reliable": reliable,
            "Recommendation": recommendation
        }
