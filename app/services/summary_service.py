from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from app.pydantic_models.summay_model import SummaryOutput

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

        # Structured output model (Pydantic)
        self.structured_llm = self.llm.with_structured_output(SummaryOutput)

        # Define the system message
        self.system_message = (
            "You are an expert video summarizer. Your task is to read the provided YouTube video transcript "
            "and the list of topics/subtopics, then create a clear, concise, and well-structured summary. "
            "⚠️ Important: Do NOT add or invent any information that is not present in the transcript. "
            "Only summarize the content given. Highlight the main ideas and key points under each topic, "
            "and remove filler or repetitive text. The output should be easy to understand, organized, "
            "and suitable for quick learning or revision."
        )

        # Build the summarizer chain once
        self.summarizer_chain = self._build_chain()

    def _build_chain(self) -> RunnableSequence:
        """
        Internal method to build the summarizer chain using RunnableSequence.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            ("human", "Transcript:\n{transcript}\n\nTopics & Subtopics:\n{topics}"),
        ])

        # Runnable sequence: prompt -> structured LLM -> structured output
        chain = prompt | self.structured_llm
        return chain

    async def generate_summary(self, transcript: str, topics: str) -> SummaryOutput:
        """
        Generate a structured summary given transcript and topics.
        Returns a Pydantic Summary object.
        """
        return await self.summarizer_chain.ainvoke({"transcript": transcript, "topics": topics})


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