import requests
import json

class PerplexityService:
    """Service for interacting with Perplexity AI API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"  # Model with online search
    
    def query(self, prompt, model=None):
        """
        Send a query to Perplexity AI
        
        Args:
            prompt: The prompt to send
            model: Optional model override
            
        Returns:
            dict with 'content' and 'citations'
        """
        if not self.api_key:
            raise ValueError("Perplexity API key is not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional equity research analyst with access to real-time market data. Always use the most current, up-to-date information available. Include today's date and current stock prices in your analysis. Provide detailed, data-driven analysis with citations and dates."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2  # Lower temperature for more factual responses
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=90  # Increased timeout
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Extract content and citations
            content = data['choices'][0]['message']['content']
            citations = data.get('citations', [])
            
            return {
                'content': content,
                'citations': citations
            }
            
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The API took too long to respond.")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', error_msg)
                except:
                    error_msg = e.response.text if e.response.text else error_msg
            raise Exception(f"API error: {error_msg}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected API response format: {str(e)}")
