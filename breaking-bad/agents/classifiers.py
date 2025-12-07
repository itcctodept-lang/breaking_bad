from .base import BaseAgent
import json

class UrgencyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="urgency_agent",
            prompt_template="""
            You are an Urgency Classifier Agent. Your goal is to determine the urgency of a news article.
            
            Persona: A veteran news editor who needs to decide if this is 'Breaking News' or 'Feature'.
            
            Analyze the following text and determine its urgency level.
            Levels: 'Immediate', 'High', 'Medium', 'Low'.
            
            Content:
            {content}
            
            Return ONLY a JSON object:
            {{
                "level": "generated_level",
                "reasoning": "brief explanation"
            }}
            """
        )

    def execute(self, news_item):
        return self._get_llm_response(news_item["content"])


class SensitivityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="sensitivity_agent",
            prompt_template="""
            You are a Sensitivity Analyzer Agent.
            
            Persona: A compliance officer ensuring content is safe and flagged if sensitive.
            
            Analyze the following text for sensitive content (political bias, violence, explicit content, etc.).
            Score from 0 (Not sensitive) to 10 (Highly sensitive).
            
            Content:
            {content}
            
            Return ONLY a JSON object:
            {{
                "score": integer_score,
                "flags": ["list", "of", "flags"],
                "reasoning": "brief explanation"
            }}
            """
        )

    def execute(self, news_item):
        return self._get_llm_response(news_item["content"])


class TopicAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="topic_agent",
            prompt_template="""
            You are a Topic Classification Agent.
            
            Persona: A librarian who categorizes information precisely.
            
            Identify the main topics and keywords of the article.
            
            Content:
            {content}
            
            Return ONLY a JSON object:
            {{
                "main_topic": "string",
                "sub_topics": ["list", "of", "strings"],
                "keywords": ["list", "of", "keywords"],
                "reasoning": "brief explanation"
            }}
            """
        )

    def execute(self, news_item):
        return self._get_llm_response(news_item["content"])


class TypeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="type_agent",
            prompt_template="""
            You are a Content Type Classifier Agent.
            
            Persona: A media analyst.
            
            Classify the type of this article.
            Types: 'Report', 'Opinion', 'Editorial', 'Satire', 'Advertisement', 'Press Release'.
            
            Content:
            {content}
            
            Return ONLY a JSON object:
            {{
                "type": "generated_type",
                "reasoning": "brief explanation"
            }}
            """
        )

    def execute(self, news_item):
        return self._get_llm_response(news_item["content"])


class RecipientAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="recipient_agent",
            prompt_template="""
            You are a Distribution Agent.
            
            Persona: A communications director who knows exactly who needs to see what.
            
            Based on the content, suggest recipients from this list:
            ['Legal', 'HR', 'PR', 'Finance', 'Engineering', 'Executive', 'All Employees'].
            
            Content:
            {content}
            
            Return ONLY a JSON object:
            {{
                "recipients": ["list", "of", "recipients"],
                "reasoning": "brief explanation"
            }}
            """
        )

    def execute(self, news_item):
        return self._get_llm_response(news_item["content"])
