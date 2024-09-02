
    


import os
import google.generativeai as genai
from django.conf import settings
from .models import ProcessedData

# Configurar a chave da API
os.environ["API_KEY"] = settings.GENERATIVE_AI_API_KEY
genai.configure(api_key=os.environ["API_KEY"])

# Configuração do modelo
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

def process_text(user, ata):
    info ={'ata':'faça isso sem seus comentários,filtre esse html puro e faça uma ata em um paragrafo único e detalhado,revise possiveis erros de ortografia, apenas! '}

    try:
        # Criação do modelo
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Iniciar uma sessão de chat
        chat_session = model.start_chat(
            history=[]
        )

        # Enviar mensagem e obter a resposta
        response = chat_session.send_message(info['ata']+ata.text)

        # Obter o texto processado
        processed_text = response.text
        print(processed_text,'\n\n\n\n')
    except Exception as e:
        processed_text = f"Erro ao processar texto: {e}"

    # Armazenar os dados processados no banco de dados
    ProcessedData.objects.create(
        user=user,
        source_id=ata.id,
        source_app='ata_model',
        processed_text=processed_text
    )
