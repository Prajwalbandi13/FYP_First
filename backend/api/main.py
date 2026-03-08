from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 🔹 LOAD ENV VARIABLES (.env)
from dotenv import load_dotenv
import os

# MUST be called BEFORE ActionAgent is created
load_dotenv()

from agents.monitoring_agent import MonitoringAgent
from agents.analyzing_agent import AnalyzingAgent
from agents.decision_agent import DecisionAgent
from agents.action_agent import ActionAgent

# ----------------------------
# FASTAPI APP
# ----------------------------
app = FastAPI(
    title="CureX – Lung Disease Detection System",
    description="Agent-based AI system for lung disease detection using Chest X-rays",
    version="1.0.0"
)

# ----------------------------
# CORS CONFIGURATION
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # OK for demo / final year project
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# AGENT INITIALIZATION
# ----------------------------
try:
    monitoring_agent = MonitoringAgent()
    analyzing_agent = AnalyzingAgent()
    decision_agent = DecisionAgent()
    action_agent = ActionAgent()
except Exception as e:
    # Fails fast if model or env is misconfigured
    raise RuntimeError(f"Agent initialization failed: {str(e)}")

# ----------------------------
# HEALTH CHECK ENDPOINT
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "CureX backend running",
        "message": "Agent-based Lung Disease Detection API is live"
    }

# ----------------------------
# MAIN PREDICTION ENDPOINT
# ----------------------------
@app.post("/detect")
async def detect_lung_disease(
    file: UploadFile = File(...),
    age: int = Form(...),
    previous_disease: str = Form("")
):
    """
    Pipeline:
    1. Monitoring Agent  -> image validation & preprocessing
    2. Analyzing Agent   -> CNN inference (MobileNetV2)
    3. Decision Agent    -> severity & confidence reasoning
    4. Action Agent      -> ethical, user-facing response
    """

    try:
        # 1️⃣ Monitoring Agent
        image = monitoring_agent.process(file)

        # 2️⃣ Analyzing Agent
        predictions = analyzing_agent.analyze(image)

        # 3️⃣ Decision Agent
        decision = decision_agent.decide(predictions)

        # 4️⃣ Action Agent
        patient_context = {
            "age": age,
            "previous_disease": previous_disease
        }
        response = action_agent.act(decision, patient_context)

        return response

    except ValueError as ve:
        # Input validation / preprocessing errors
        raise HTTPException(status_code=400, detail=str(ve))

    except FileNotFoundError as fe:
        # Model file missing
        raise HTTPException(status_code=500, detail=str(fe))

    except RuntimeError as re:
        # Gemini / env / agent init errors
        raise HTTPException(status_code=500, detail=str(re))

    except Exception as e:
        # Catch-all safety net
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
