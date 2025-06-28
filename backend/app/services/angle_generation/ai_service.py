"""
AI service for trend analysis and campaign generation.
Supports OpenRouter, OpenAI, and Anthropic providers.
"""

from typing import List, Dict, Any, Optional
import json
import asyncio
import aiohttp
import structlog
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from ...core.config import settings
from ...models.trend import Trend

logger = structlog.get_logger()


class AIProvider:
    """Base class for AI providers."""
    
    async def generate_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate completion from messages."""
        raise NotImplementedError


class OpenRouterProvider(AIProvider):
    """OpenRouter AI provider supporting multiple models."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion using OpenRouter."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenRouter completion failed", error=str(e), model=model)
            raise


class OpenAIProvider(AIProvider):
    """Direct OpenAI provider."""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI completion failed", error=str(e), model=model)
            raise


class AnthropicProvider(AIProvider):
    """Direct Anthropic provider."""
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion using Anthropic."""
        try:
            # Convert OpenAI format to Anthropic format
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or "You are a helpful assistant.",
                messages=user_messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error("Anthropic completion failed", error=str(e), model=model)
            raise


class AIService:
    """Multi-provider AI service for trend analysis and campaign generation."""
    
    def __init__(self):
        """Initialize AI service with available providers."""
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider = settings.DEFAULT_AI_PROVIDER
        
        # Initialize available providers
        if settings.OPENROUTER_API_KEY:
            self.providers["openrouter"] = OpenRouterProvider(settings.OPENROUTER_API_KEY)
            logger.info("OpenRouter provider initialized")
        
        if settings.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider(settings.OPENAI_API_KEY)
            logger.info("OpenAI provider initialized")
        
        if settings.ANTHROPIC_API_KEY:
            self.providers["anthropic"] = AnthropicProvider(settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic provider initialized")
        
        if not self.providers:
            logger.warning("No AI providers configured - using fallback templates only")
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[AIProvider]:
        """Get AI provider by name or default."""
        provider_name = provider_name or self.default_provider
        return self.providers.get(provider_name)
    
    async def generate_with_fallback(
        self, 
        messages: List[Dict[str, str]], 
        primary_model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate completion with automatic fallback."""
        primary_model = primary_model or settings.DEFAULT_AI_MODEL
        fallback_model = fallback_model or settings.BACKUP_AI_MODEL
        
        # Try primary provider/model
        try:
            if self.default_provider in self.providers:
                provider = self.providers[self.default_provider]
                result = await provider.generate_completion(
                    messages, model=primary_model, **kwargs
                )
                logger.info("AI completion successful", provider=self.default_provider, model=primary_model)
                return result
        except Exception as e:
            logger.warning("Primary AI provider failed", error=str(e), provider=self.default_provider)
        
        # Try fallback providers
        for provider_name, provider in self.providers.items():
            if provider_name == self.default_provider:
                continue  # Already tried
            
            try:
                # Adjust model name for different providers
                model = self._adjust_model_for_provider(fallback_model, provider_name)
                result = await provider.generate_completion(
                    messages, model=model, **kwargs
                )
                logger.info("AI fallback successful", provider=provider_name, model=model)
                return result
            except Exception as e:
                logger.warning("Fallback AI provider failed", error=str(e), provider=provider_name)
        
        raise Exception("All AI providers failed")
    
    def _adjust_model_for_provider(self, model: str, provider: str) -> str:
        """Adjust model name for specific provider."""
        if provider == "openrouter":
            # OpenRouter uses provider/model format
            if "/" not in model:
                if "gpt" in model.lower():
                    return f"openai/{model}"
                elif "claude" in model.lower():
                    return f"anthropic/{model}"
            return model
        elif provider == "openai":
            # Extract just the model name for OpenAI
            if "/" in model:
                return model.split("/")[-1]
            return model
        elif provider == "anthropic":
            # Extract just the model name for Anthropic
            if "/" in model:
                return model.split("/")[-1]
            return model
        
        return model
    
    async def analyze_trend_sustainability(self, trend: Trend) -> Dict[str, Any]:
        """
        Analyze trend sustainability using AI.
        
        Args:
            trend: Trend object to analyze
            
        Returns:
            Dictionary with sustainability analysis
        """
        if not self.providers:
            logger.warning("No AI providers configured, using fallback")
            return self._fallback_sustainability_analysis(trend)
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert PR analyst specializing in trend analysis and campaign sustainability. Respond only in valid JSON format."
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze the sustainability of this trending topic for PR campaigns:
                    
                    Title: {trend.title}
                    Description: {trend.description or 'No description'}
                    Source: {trend.source}
                    Platforms: {', '.join(trend.platforms)}
                    Current Score: {trend.score}
                    Keywords: {', '.join(trend.keywords) if trend.keywords else 'None'}
                    
                    Provide a sustainability score (0.0-1.0) and brief analysis focusing on:
                    1. How long this trend might last (days/weeks/months)
                    2. PR campaign potential (high/medium/low)
                    3. Brand safety considerations
                    4. Recommended campaign timing
                    
                    Respond in JSON format with:
                    {{
                        "score": float,
                        "longevity": "short|medium|long",
                        "pr_potential": "high|medium|low",
                        "safety_notes": string,
                        "recommended_timing": string,
                        "risk_factors": [list of strings]
                    }}
                    """
                }
            ]
            
            response = await self.generate_with_fallback(
                messages,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse JSON response
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON", response=response)
                return self._fallback_sustainability_analysis(trend)
            
        except Exception as e:
            logger.warning("AI sustainability analysis failed", error=str(e))
            return self._fallback_sustainability_analysis(trend)
    
    async def check_brand_safety(self, trend: Trend) -> Dict[str, Any]:
        """
        Check brand safety of a trend.
        
        Args:
            trend: Trend to check
            
        Returns:
            Dictionary with safety assessment
        """
        # Simple heuristic brand safety check
        unsafe_keywords = [
            'scandal', 'controversy', 'death', 'accident', 'crime', 'violence',
            'lawsuit', 'arrest', 'fraud', 'scam', 'hate', 'discrimination'
        ]
        
        title_lower = trend.title.lower()
        is_safe = not any(keyword in title_lower for keyword in unsafe_keywords)
        
        return {
            'is_safe': is_safe,
            'confidence': 0.8 if is_safe else 0.2,
            'risk_factors': [kw for kw in unsafe_keywords if kw in title_lower]
        }
    
    async def generate_campaign_ideas(self, trend: Trend) -> List[Dict[str, Any]]:
        """
        Generate campaign ideas for a trend using AI and fallback templates.
        
        Args:
            trend: Trend to generate campaigns for
            
        Returns:
            List of campaign idea dictionaries
        """
        # Try AI generation first
        if self.providers:
            try:
                ai_ideas = await self._generate_ai_campaign_ideas(trend)
                if ai_ideas:
                    return ai_ideas
            except Exception as e:
                logger.warning("AI campaign generation failed, using templates", error=str(e))
        
        # Fallback to template-based generation
        return self._generate_template_campaign_ideas(trend)
    
    async def _generate_ai_campaign_ideas(self, trend: Trend) -> List[Dict[str, Any]]:
        """Generate campaign ideas using AI."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert PR strategist and campaign ideation specialist. 
                Generate creative, actionable PR campaign ideas based on trending topics. 
                Focus on campaigns that can be executed within 1-7 days and have strong media potential.
                Respond only in valid JSON format."""
            },
            {
                "role": "user",
                "content": f"""
                Generate 3 diverse PR campaign ideas for this trending topic:
                
                Title: {trend.title}
                Description: {trend.description or 'No description available'}
                Source: {trend.source}
                Platforms: {', '.join(trend.platforms)}
                Current Score: {trend.score}
                Keywords: {', '.join(trend.keywords) if trend.keywords else 'None'}
                
                For each campaign idea, provide:
                
                1. A reactive/newsjacking campaign (quick response, 1-2 days)
                2. A data-driven thought leadership campaign (2-3 days)  
                3. A creative/viral angle campaign (3-5 days)
                
                Respond in JSON format:
                {{
                    "campaigns": [
                        {{
                            "title": "Campaign title",
                            "headline": "Media-ready headline",
                            "description": "Brief description",
                            "brief": "Detailed execution brief",
                            "type": "reactive|data-driven|creative",
                            "target_audience": "Primary audience",
                            "timeline": "X days",
                            "difficulty": "easy|medium|hard",
                            "potential_score": 0.0-1.0,
                            "virality_score": 0.0-1.0,
                            "brand_safety_score": 0.0-1.0,
                            "channels": ["list", "of", "channels"],
                            "key_messages": ["message1", "message2"],
                            "media_hooks": ["hook1", "hook2"],
                            "execution_steps": ["step1", "step2", "step3"]
                        }}
                    ]
                }}
                """
            }
        ]
        
        response = await self.generate_with_fallback(
            messages,
            max_tokens=2000,
            temperature=0.8
        )
        
        try:
            result = json.loads(response)
            campaigns = result.get("campaigns", [])
            
            # Validate and enrich each campaign
            validated_campaigns = []
            for campaign in campaigns:
                if self._validate_campaign_structure(campaign):
                    campaign["model"] = "ai-generated"
                    campaign["generated_at"] = "2024-01-01T00:00:00Z"  # Would use actual timestamp
                    validated_campaigns.append(campaign)
            
            return validated_campaigns
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI campaign response", error=str(e), response=response)
            return []
    
    def _validate_campaign_structure(self, campaign: Dict[str, Any]) -> bool:
        """Validate campaign structure has required fields."""
        required_fields = [
            "title", "headline", "description", "brief", "type", 
            "target_audience", "timeline", "difficulty"
        ]
        return all(field in campaign for field in required_fields)
    
    def _generate_template_campaign_ideas(self, trend: Trend) -> List[Dict[str, Any]]:
        """Generate campaign ideas using templates as fallback."""
        ideas = []
        
        # Reactive/Newsjacking campaign
        ideas.append({
            'title': f"Breaking: {trend.title} - Industry Response",
            'headline': f"How {trend.title} is Reshaping the Conversation",
            'description': f"Immediate response to trending topic '{trend.title}' with industry perspective",
            'brief': f"Quick-turnaround reactive campaign positioning your brand as a thought leader responding to {trend.title}. Focus on timely, relevant commentary that adds value to the trending conversation.",
            'type': 'reactive',
            'target_audience': 'Industry professionals and media',
            'timeline': '1-2 days',
            'difficulty': 'easy',
            'potential_score': 0.7,
            'virality_score': 0.8,
            'brand_safety_score': 0.8,
            'channels': ['social-media', 'press-release', 'blog'],
            'key_messages': [
                f"Expert perspective on {trend.title}",
                "Timely industry insight",
                "Thought leadership positioning"
            ],
            'media_hooks': [
                f"Industry expert responds to {trend.title}",
                "Real-time analysis and commentary",
                "Expert predictions and implications"
            ],
            'execution_steps': [
                "Monitor trend development",
                "Craft expert commentary",
                "Distribute across channels"
            ],
            'model': 'template-based'
        })
        
        # Data-driven campaign
        ideas.append({
            'title': f"Data Deep-Dive: {trend.title} Impact Analysis",
            'headline': f"The Numbers Behind {trend.title}: What the Data Reveals",
            'description': f"Data-driven analysis of {trend.title} trends and implications",
            'brief': f"Create compelling data story around {trend.title} using research, surveys, or analysis. Perfect for establishing thought leadership and generating media interest through exclusive insights.",
            'type': 'data-driven',
            'target_audience': 'Business leaders and media',
            'timeline': '2-3 days',
            'difficulty': 'medium',
            'potential_score': 0.8,
            'virality_score': 0.6,
            'brand_safety_score': 0.9,
            'channels': ['press-release', 'reports', 'social-media'],
            'key_messages': [
                f"Exclusive data on {trend.title}",
                "Research-backed insights",
                "Industry implications"
            ],
            'media_hooks': [
                f"First comprehensive analysis of {trend.title}",
                "Exclusive survey results",
                "Data-driven predictions"
            ],
            'execution_steps': [
                "Gather relevant data/conduct research",
                "Create compelling visualizations",
                "Package for media distribution"
            ],
            'model': 'template-based'
        })
        
        # Creative/Viral campaign
        ideas.append({
            'title': f"Creative Spin: {trend.title} Reimagined",
            'headline': f"What {trend.title} Teaches Us About [Your Industry]",
            'description': f"Creative angle connecting {trend.title} to broader industry themes",
            'brief': f"Develop a unique, creative angle that connects {trend.title} to your industry or expertise in an unexpected way. Focus on viral potential and memorable messaging.",
            'type': 'creative',
            'target_audience': 'Broad audience and social media',
            'timeline': '3-5 days',
            'difficulty': 'hard',
            'potential_score': 0.6,
            'virality_score': 0.9,
            'brand_safety_score': 0.7,
            'channels': ['social-media', 'video', 'interactive-content'],
            'key_messages': [
                f"Unique perspective on {trend.title}",
                "Creative industry connection",
                "Memorable brand moment"
            ],
            'media_hooks': [
                f"Unexpected angle on {trend.title}",
                "Creative campaign launch",
                "Viral content potential"
            ],
            'execution_steps': [
                "Develop creative concept",
                "Create engaging content",
                "Launch viral campaign"
            ],
            'model': 'template-based'
        })
        
        return ideas
    
    def _fallback_sustainability_analysis(self, trend: Trend) -> Dict[str, Any]:
        """Fallback heuristic sustainability analysis."""
        # Simple heuristic based on trend properties
        base_score = trend.score * 0.5
        
        # Boost for certain categories
        category_boost = 0.2 if trend.category in ['technology', 'entertainment', 'business'] else 0.0
        
        # Boost for multiple platforms
        platform_boost = min(0.3, len(trend.platforms) * 0.1)
        
        sustainability_score = min(1.0, base_score + category_boost + platform_boost)
        
        return {
            'score': sustainability_score,
            'longevity': 'medium' if sustainability_score > 0.5 else 'short',
            'pr_potential': 'high' if sustainability_score > 0.7 else 'medium',
            'safety_notes': 'Automated heuristic analysis',
            'method': 'fallback_heuristic'
        } 