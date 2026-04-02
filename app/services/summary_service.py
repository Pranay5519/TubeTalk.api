from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from app.pydantic_models.summay_model import SummaryOutput, CombinedStudyOutput

class SummaryGenerator:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        """
        Initialize the Summary Generator with a chosen LLM.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )

        # Structured output models
        self.structured_llm = self.llm.with_structured_output(SummaryOutput)
        self.combined_llm = self.llm.with_structured_output(CombinedStudyOutput)

        # System message for combined topics and summary
        self.combined_system_message = (
            "You are an expert video analyzer and summarizer. Your task is to perform two actions on the provided YouTube transcript:\n"
            "1. EXTRACT TOPICS: Identify all main topics and subtopics discussed in the video. Include their start timestamps (seconds).\n"
            "2. GENERATE SUMMARY: For each extracted topic and subtopic, provide a clear, concise, and well-structured summary.\n\n"
            "⚠️ Important:\n"
            "- Do NOT add or invent any information that is not present in the transcript.\n"
            "- KEEP the structure consistent and matched between 'topics' and 'summary' sections.\n"
            "- Use the provided (timestamp) markers in the transcript to assign accurate timestamps (in seconds)."
        )

    async def generate_summary(self, transcript: str, topics: str) -> SummaryOutput:
        """
        Generate a structured summary given transcript and topics.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert video summarizer. Create a summary based on the provided topics and transcript."),
            ("human", "Transcript:\n{transcript}\n\nTopics & Subtopics:\n{topics}"),
        ])
        chain = prompt | self.structured_llm
        return await chain.ainvoke({"transcript": transcript, "topics": topics})

    async def generate_topics_and_summary(self, transcript: str) -> CombinedStudyOutput:
        """
        One-pass method: Extract Topics AND Generate Summary from a single prompt.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.combined_system_message),
            ("human", "Here is the YouTube transcript with timestamps:\n{transcript}"),
        ])
        chain = prompt | self.combined_llm
        return await chain.ainvoke({"transcript": transcript})


# ------------------- Runner -------------------

"""import asyncio
import os
from fastapi import HTTPException

from app.services.topics_service import TopicGenerator
from app.services.summary_service import SummaryGenerator
from app.utils.utility_functions import load_transcript
from app.pydantic_models.topics_model import TopicsOutput

api_key = os.environ["GOOGLE_API_KEY"]
url = "https://youtu.be/TVUibwoVXZc"


if __name__ == "__main__":
    async def main():
        generator = SummaryGenerator(api_key=api_key)
        analyzer = TopicGenerator(api_key=api_key)

        # Load transcript
        captions = load_transcript(url)
        print("\n🎬 Loaded Transcript")
        print("==" * 20)
Sorry sorry
        if not captions:
            raise HTTPException(status_code=404, detail="No transcript found for this video.")

        # Parse transcript into segments
        segments = analyzer.parse_transcript(captions)
        formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]

        # Extract topics (async call)
        response = await analyzer.extract_topics(" ".join(formatted))
        if not response:
            raise HTTPException(status_code=500, detail="Failed to extract topics.")

        # Convert to Pydantic model
        topics_output = TopicsOutput(main_topics=response.main_topics)

        print("\n🗂️ Extracted Topics & Subtopics")
        print(topics_output.model_dump_json(indent=2))
        print("==" * 20)

        # Generate summary
        summary = await generator.generate_summary(captions, topics_output.model_dump_json())
        print("==" * 30)
        print("\n📘 Generated Summary:\n", summary.model_dump_json(indent=2))

    asyncio.run(main())
"""