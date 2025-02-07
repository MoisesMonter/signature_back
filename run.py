import re

#Resposta de Ollama

resposta = resposta["mensagem"]["conteúdo"]

# Remover Think Tag do texto com expressões regulares

limpo_content = re.sub(r"<think>.*?</think>\n?", "",

resposta, sinalizadores = re.DOTALL)