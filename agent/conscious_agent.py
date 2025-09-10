import os
import json
from typing import Dict, Any
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

class ConsciousAgent:
    def __init__(self, model_name="meta-llama/llama-3.1-8b-instruct", temperature=0.7):
        """Initialize the agent with OpenRouter and tools"""
        self.api_key = self.get_api_key()
        self.llm = self.create_llm(model_name, temperature)
        
        tools = self.create_reflection_tools()
        
        # Use LangChain Hub default ReAct prompt
        base_prompt = hub.pull("hwchase17/react")
        
        # Create agent with proper prompt
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=base_prompt,
        )
        
        # Wrap agent in executor
        self.agent = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10)

    def get_api_key(self):
        """Fetch API key from environment (OpenRouter key)"""
        api_key = os.getenv("openrouter_api_key")
        
        if not api_key:
            raise ValueError("❌ openrouter_api_key not set in environment.")
        return api_key

    def create_llm(self, model_name, temperature):
        """Create LLM instance for OpenRouter"""
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=1200,
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Conscious Day Agent"
            }
        )

    def create_reflection_tools(self):
        """Define custom tools for reflection processing"""

        def analyze_emotions(input_str: str) -> str:
            """Analyze emotional state from journal text"""
            prompt = f"""
            Analyze the emotional state and underlying feelings in this journal entry: {input_str}
            
            Focus on:
            - Current emotional state
            - Underlying patterns or themes
            - What the words reveal about their mindset
            
            Provide a compassionate 2-3 sentence analysis.
            """
            response = self.llm.invoke(prompt)
            return response.content

        def interpret_dream(input_str: str) -> str:
            """Interpret dream symbolism and meaning"""
            if not input_str or input_str.strip().lower() in ["", "no dream", "none", "no dream shared"]:
                return "No dream shared today. Rest and subconscious processing remain valuable for mental clarity and emotional balance."
            
            prompt = f"""
            Provide a thoughtful dream interpretation for: {input_str}
            
            Focus on:
            - Symbolic meanings
            - Emotional themes
            - Potential connections to waking life
            
            Provide a 2-3 sentence interpretation.
            """
            response = self.llm.invoke(prompt)
            return response.content

        def create_strategy(input_str: str) -> str:
            """Create time-aware daily strategy"""
            try:
                data = json.loads(input_str)
                intention = data.get("intention", "")
                priorities = data.get("priorities", "")
                emotional_state = data.get("emotional_state", "")
            except Exception:
                # If not JSON, treat as simple string
                parts = input_str.split("|")
                intention = parts[0] if len(parts) > 0 else input_str
                priorities = parts[1] if len(parts) > 1 else ""
                emotional_state = parts[2] if len(parts) > 2 else ""

            prompt = f"""
            Create a practical daily strategy based on:
            - Intention: {intention}
            - Priorities: {priorities}
            - Emotional State: {emotional_state}
            
            Provide:
            - Time-aware task suggestions
            - What to focus on and what to avoid
            - How to maintain the desired mindset
            
            Give a 3-4 sentence practical strategy.
            """
            response = self.llm.invoke(prompt)
            return response.content

        def create_mindset_insight(input_str: str) -> str:
            """Generate mindset insight based on all inputs"""
            try:
                data = json.loads(input_str)
                intention = data.get("intention", "")
                emotional_state = data.get("emotional_state", "")
                dream_analysis = data.get("dream_analysis", "")
            except Exception:
                parts = input_str.split("|")
                intention = parts[0] if len(parts) > 0 else input_str
                emotional_state = parts[1] if len(parts) > 1 else ""
                dream_analysis = parts[2] if len(parts) > 2 else ""

            prompt = f"""
            Based on this information:
            - Intention: {intention}
            - Emotional State: {emotional_state}
            - Dream Analysis: {dream_analysis}
            
            Provide a mindset insight that:
            - Connects intention to current emotional state
            - Suggests mindset shifts or awareness
            - Encourages balance and self-awareness
            
            Give a 2-3 sentence insight.
            """
            response = self.llm.invoke(prompt)
            return response.content

        return [
            Tool(
                name="analyze_emotions",
                func=analyze_emotions,
                description="Analyze emotions and mental state from journal text"
            ),
            Tool(
                name="interpret_dream",
                func=interpret_dream,
                description="Interpret symbolic meaning and emotions in dreams"
            ),
            Tool(
                name="create_strategy",
                func=create_strategy,
                description="Create time-aware daily strategy. Input: JSON with intention, priorities, emotional_state"
            ),
            Tool(
                name="create_mindset_insight",
                func=create_mindset_insight,
                description="Generate mindset insight. Input: JSON with intention, emotional_state, dream_analysis"
            )
        ]

    def process_reflection(self, journal: str, dream: str, intention: str, priorities: str) -> Dict[str, str]:
        """Process reflection using agent in a single comprehensive call"""
        
        # Create comprehensive input for single agent call
        comprehensive_input = f"""
        Please process this morning reflection using your available tools:
        
        Journal: {journal}
        Dream: {dream or 'No dream shared'}
        Intention: {intention}
        Priorities: {priorities}
        
        Instructions:
        1. First, use analyze_emotions on the journal entry
        2. Then, use interpret_dream on the dream
        3. Then, use create_strategy with JSON input containing intention, priorities, and the emotional analysis
        4. Finally, use create_mindset_insight with JSON input containing intention, emotional analysis, and dream analysis
        
        Provide your final answer in exactly this format:
        
        **INNER REFLECTION:**
        [Results from analyze_emotions]
        
        **DREAM INTERPRETATION:**
        [Results from interpret_dream]
        
        **MINDSET INSIGHT:**
        [Results from create_mindset_insight]
        
        **DAY STRATEGY:**
        [Results from create_strategy]
        """
        
        # Single agent call
        response = self.agent.invoke({"input": comprehensive_input})
        
        # Parse the response
        return self._parse_response(response["output"])

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse the agent response into structured sections"""
        
        sections = {
            'reflection': '',
            'dream_interpretation': '',
            'mindset_insight': '',
            'strategy': ''
        }
        
        # Split by section headers
        parts = response.split('**')
        
        current_section = None
        for part in parts:
            part = part.strip()
            
            if 'INNER REFLECTION:' in part.upper():
                current_section = 'reflection'
                content = part.replace('INNER REFLECTION:', '').replace('Inner Reflection:', '').strip()
                sections[current_section] = content
            elif 'DREAM INTERPRETATION:' in part.upper():
                current_section = 'dream_interpretation'
                content = part.replace('DREAM INTERPRETATION:', '').replace('Dream Interpretation:', '').strip()
                sections[current_section] = content
            elif 'MINDSET INSIGHT:' in part.upper():
                current_section = 'mindset_insight'
                content = part.replace('MINDSET INSIGHT:', '').replace('Mindset Insight:', '').strip()
                sections[current_section] = content
            elif 'DAY STRATEGY:' in part.upper():
                current_section = 'strategy'
                content = part.replace('DAY STRATEGY:', '').replace('Day Strategy:', '').strip()
                sections[current_section] = content
            elif current_section and part and not any(header in part.upper() for header in ['INNER REFLECTION:', 'DREAM INTERPRETATION:', 'MINDSET INSIGHT:', 'DAY STRATEGY:']):
                # Continue adding to current section
                if sections[current_section]:
                    sections[current_section] += ' ' + part
                else:
                    sections[current_section] = part

        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
            # Remove bracket placeholders if present
            if sections[key].startswith('[') and sections[key].endswith(']'):
                sections[key] = sections[key][1:-1].strip()
        
        return sections