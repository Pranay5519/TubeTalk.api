from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence


class SummaryGenerator:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        """
        Initialize the Summary Generator with a chosen LLM.
        """
        self.model_name = model_name
        self.temperature = temperature

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=self.temperature)

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
        Internal method to build the summarizer chain using RunnableSequence (LCEL).
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            ("human", "Transcript:\n{transcript}\n\nTopics & Subtopics:\n{topics}"),
        ])

        # Runnable sequence: prompt -> model -> string output
        chain = prompt | self.llm | (lambda x: x.content if hasattr(x, "content") else str(x))
        return chain

    async def generate_summary(self, transcript: str, topics: str) -> str:
        """
        Generate a structured summary given transcript and topics.
        """
        return await self.summarizer_chain.ainvoke({"transcript": transcript, "topics": topics})

from app.services.topics_service import TopicGenerator
from app.utils.utility_functions import load_transcript
import asyncio

"""if __name__ == "__main__":
    async def main():
        generator = SummaryGenerator()
        analyzer = TopicGenerator()
        
        transcript_text = load_transcript("https://youtu.be/TVUibwoVXZc")
        print("\n🎬 Loaded Transcript")
        print("==" * 20)

        if transcript_text:
            segments = analyzer.parse_transcript(transcript_text)
            formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]
            topics_text = analyzer.extract_topics(" ".join(formatted))
            print("\n🗂️ Extracted Topics & Subtopics")
            print(topics_text)
            print("==" * 20)

            summary = await generator.generate_summary(transcript_text, topics_text)
            print("\n📘 Generated Summary:\n", summary)

    asyncio.run(main())"""
