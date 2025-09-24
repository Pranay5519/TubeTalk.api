from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from ..models.topics_model import TopicsOutput 
import re
from dotenv import load_dotenv
load_dotenv()
from app.utils.utility_functions import load_transcript
# -------------------------
# Data Classes for Transcript
# -------------------------
@dataclass
class TimestampedSegment:
    """Represents a segment of transcript with timestamp"""
    text: str
    start_time: float
    end_time: float = None

# -------------------------
# Transcript Analyzer Class (OOP)
# -------------------------
class TopicGenerator:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.0):
        # Initialize AI model
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

        # Setup parser
        self.parser = PydanticOutputParser(pydantic_object=TopicsOutput)
        self.format_instructions = self.parser.get_format_instructions()

        # Create system and human prompts
        self.system_message = SystemMessagePromptTemplate.from_template(
            """You are an expert in analyzing and structuring video transcripts.

        You will receive a transcript of a YouTube video with timestamps.

        Your task is to:
        1. Extract all MAIN TOPICS discussed in the transcript.
        2. For each MAIN TOPIC, list its SUBTOPICS in a hierarchical structure.
        3. Always include timestamp references (in seconds) for both MAIN TOPICS and SUBTOPICS.
        4. For each subtopic, optionally add an 'importance' (high/medium/low) if it is clearly emphasized.
        5. Be concise and only include material that is actually discussed in the transcript.
        6. Output must be valid JSON and match the schema instructions below.

        REQUIRED OUTPUT FORMAT:
        {format_instructions}
        """,
            partial_variables={"format_instructions": self.format_instructions}
        )

        self.human_message = HumanMessagePromptTemplate.from_template(
                            """Transcript:
                {transcript}

                Notes:
                - Use timestamps in seconds (floats allowed).
                - Only include main topics and subtopics actually present in the transcript.
                - If something is unclear, omit it rather than inventing timestamps.

                Now extract main topics and subtopics."""
                        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message, self.human_message]
        )


    # -------------------------
    # Transcript Parsing
    # -------------------------
    def parse_transcript(self, transcript: str) -> List[TimestampedSegment]:
        """Split transcript into timestamped segments"""
        segments = []
        pattern = r"(.*?)\((\d+\.?\d*)\)"
        matches = re.findall(pattern, transcript)

        for i, (text, timestamp) in enumerate(matches):
            text = text.strip()
            if text:
                segment = TimestampedSegment(
                    text=text,
                    start_time=float(timestamp),
                    end_time=float(matches[i + 1][1]) if i + 1 < len(matches) else None,
                )
                segments.append(segment)

        return segments

    # -------------------------
    # Topic Extraction with LLM
    # -------------------------
    def extract_topics(self, transcript: str) -> TopicsOutput:
        """Extract structured topics from transcript using LLM"""
        prompt = self.chat_prompt.format_prompt(
            transcript=transcript, format_instructions=self.format_instructions
        )
        messages = prompt.to_messages()

        response_message = self.model.invoke(messages)
        raw_output = response_message.content

        if isinstance(raw_output, list):
            raw_output = " ".join(raw_output)

        clean_output = raw_output.strip()
        if clean_output.startswith("```"):
            clean_output = clean_output.strip("`").split("\n", 1)[-1]

        return self.parser.parse(clean_output)


# -------------------------
# Example Runner
# -------------------------
"""if __name__ == "__main__":
    analyzer = TopicGenerator()

    captions = load_transcript("https://youtu.be/ikzN6byFNWw")
    if captions:
        segments = analyzer.parse_transcript(captions)
        formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]
        response = analyzer.extract_topics(" ".join(formatted))

        # Pretty print
        for i, topic in enumerate(response.main_topics, 1):
            print(f"\n🎯 Main Topic {i}: {topic.topic}  ⏰ {topic.timestamp}")
            print("----------------------------------------------------")
            for j, sub in enumerate(topic.subtopics, 1):
                print(f"   🔹 Subtopic {i}.{j}: {sub.subtopic}  ⏰ {sub.timestamp} {sub.importance}")
            print("====================================================")"""
