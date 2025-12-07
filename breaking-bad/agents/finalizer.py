from .base import BaseAgent
import json
import logging

class FinalizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="finalizer_agent",
            prompt_template="""
            You are the Finalizer Agent.
            
            Persona: A Chief Editor and Safety Officer. You have the final say.
            
            Your task is to:
            1. Aggregate the results from all other agents.
            2. Resolve any conflicts (e.g., if Urgency is High but Recipient is None).
            3. Apply safety controls (ensure no highly sensitive content goes to 'All Employees').
            4. Finalize the recipient list and metadata.
            
            Original Content:
            {content}
            
            Agents Results:
            {agents_results}
            
            Return ONLY a JSON object:
            {{
                "is_safe": true/false,
                "final_recipients": ["list"],
                "final_urgency": "string",
                "final_classification": "string",
                "summary": "one sentence summary",
                "notes": "any conflict resolution notes"
            }}
            """
        )

    def execute(self, news_item):
        # Gather results from the news_item dictionary which acts as our shared state
        agents_results = news_item.get("agents_results", {})
        
        # Prepare context for the LLM
        context = {
            "content": news_item["content"],
            "agents_results": json.dumps(agents_results, indent=2)
        }
        
        # We need to custom format because our base prompt expects just 'content'
        # But here we are passing a more complex prompt.
        # So we override the _get_llm_response logic slightly or just construct the string here.
        
        full_prompt = self.prompt_template.format(**context)
        
        try:
            response = self.model.generate_content(full_prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            return json.loads(text)
        except Exception as e:
            logging.error(f"Error in Finalizer: {e}")
            return {
                "is_safe": False,
                "final_recipients": [],
                "error": str(e)
            }
