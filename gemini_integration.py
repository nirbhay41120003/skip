import google.generativeai as genai

class GeminiIntegration:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_response(self, prompt, context=""):
        try:
            full_prompt = f"{context}\n\nUSER QUESTION: {prompt}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"