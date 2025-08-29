# Analisis de comentarios de Youtube con Gemini IA
Este proyecto utiliza Python, la API de Youtube y modelos de Gemini para **analizar comentarios de un video de YouTube** y **detectar automáticamente los videojuegos más mencionados o solicitados por la audiencia**.

---
## Qué hace este proyecto??

1.  Extrae hasta 200 comentarios de un video público de YouTube.
2.  Usa IA para interpretar el contenido y detectar nombres de videojuegos, incluso con errores ortográficos.
3.  Guarda los resultados en un archivo `.csv`, incluyendo:
   - Nombre del juego
   - Número de menciones
   - Título del video
   - ID del video
4. Permite analizar múltiples videos y acumular los datos sin sobreescribir los anteriores.

---
## Tecnologías usadas
- Python 3.10+
- Google Gemini API (generative language)
- YouTube Data API v3
- Pandas
- dotenv
- re (expresiones regulares)

---
 Variables de entorno requeridas
Colocar tus claves API en archivos .env separados:

- GEMINI_API_KEY=tu_clave_gemini
- YOUTUBE_API_KEY=tu_clave_youtube

Clonar repositorio

Instalar dependencias

Ejecutar script:
python analisis_comentarios.py

---
El codigo no se limita a contar palabras: interpreta el contexto y detecta menciones difusas o con errores.
Es acumulativo: podés analizar muchos videos distintos sin perder los datos anteriores.
Fácil de adaptar para otros contextos como películas, productos, series, etc.


