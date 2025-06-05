import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,constr
from transformers import pipeline
from huggingface_hub import login
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

# Logs y advertencias python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener el token
hf_token = os.environ.get("HF_TOKEN")

if not hf_token:
    logger.error("No se encontró la variable de entorno HF_TOKEN.")
    raise ValueError("No se encontró la variable de entorno HF_TOKEN.")

# Autenticación de Hugginface
try:
    login(token=hf_token)
    logger.info("Autenticación con Hugging Face exitosa.")
except Exception as e:
    logger.error(f"Error en autenticación: {e}")
    raise

# Inicializar FastAPI
app = FastAPI()

# Cargar modelo
try:
    classifier = pipeline(
        "text-classification",
        model="pedrojm/modelv2_clasificacioncomentario"
    )
    logger.info("Modelo cargado correctamente.")
except Exception as e:
    logger.error(f"No se pudo cargar el modelo: {e}")
    raise RuntimeError(f"No se pudo cargar el modelo: {e}")

# Ruta raíz para evitar error 404
@app.get("/")
def root():
    return {"message": "API funcionando."}

# Esquema de entrada
class CommentRequest(BaseModel):
     text: Optional[str]

# Ruta de predicción
@app.post("/predict")
def clasificar_comentario(data: CommentRequest):
    if not data.text or not data.text.strip():
        raise HTTPException(
            status_code=400,
            detail="El campo 'text' no puede estar vacío o ser null."
        )
    try:
        logger.info(f"Recibido texto para clasificar: {data.text}")
        resultado = classifier(data.text)
        etiqueta = resultado[0]["label"]
        score = resultado[0]["score"]
        logger.info(f"Clasificación: {etiqueta} con confianza {score}")
        return {
            "etiqueta": etiqueta,
            "confianza": round(score, 4)
        }
    except Exception as e:
        logger.error(f"Error al clasificar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al clasificar: {str(e)}")


# Solo necesario si lo pruebas localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860)
