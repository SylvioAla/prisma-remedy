
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuración de Remedy desde variables de entorno
REMEDY_API_URL = os.getenv("REMEDY_API_URL", "http://<remedy-server>:8008/api/arsys/v1/entry/HPD:IncidentInterface_Create")
REMEDY_AUTH_TOKEN = os.getenv("REMEDY_AUTH_TOKEN", "<tu_token_de_remedy>")

@app.route('/webhook/prisma', methods=['POST'])
def recibir_alerta():
    try:
        alerta = request.json

        # Extraer datos relevantes
        descripcion = alerta.get("details", "Alerta desde Prisma Cloud")
        severidad = alerta.get("severity", "Medium")
        politica = alerta.get("policyName", "Política desconocida")
        origen = alerta.get("host", "Prisma Cloud")

        # Mapear severidad a urgencia de Remedy
        severidad_map = {
            "Low": "3-Low",
            "Medium": "3-Low",
            "High": "2-High",
            "Critical": "1-Critical"
        }
        urgencia = severidad_map.get(severidad, "3-Low")

        # Crear payload para Remedy
        payload_remedy = {
            "values": {
                "Description": f"{descripcion} (Política: {política})",
                "Urgency": urgencia,
                "Impact": "2-Significant/Large",
                "Company": "TuEmpresa",
                "Assigned Group": "Soporte TI",
                "Status": "New",
                "Reported Source": "Monitoring",
                "First_Name": "Prisma",
                "Last_Name": "Cloud",
                "Service_Type": "User Service Restoration"
            }
        }

        headers_remedy = {
            "Content-Type": "application/json",
            "Authorization": f"AR-JWT {REMEDY_AUTH_TOKEN}"
        }

        # Enviar a Remedy
        remedy_response = requests.post(REMEDY_API_URL, json=payload_remedy, headers=headers_remedy)

        return jsonify({
            "remedy_status": remedy_response.status_code,
            "remedy_response": remedy_response.text
        }), remedy_response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
