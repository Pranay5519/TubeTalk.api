from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.pydantic_models.quiz_model import QuizList
from app.utils.utility_functions import load_transcript
import asyncio


class QuizGenerator:
    """
    A class-based generator for creating multiple-choice quizzes 
    from YouTube transcripts using Gemini models.
    """

    def __init__(self, api_key : str,model_name: str = "gemini-2.5-flash", temperature: float = 0):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model=self.model_name,
                                          temperature=self.temperature,
                                          api_key=self.api_key)
        # System message for quiz generation
        self.system_template = """You are QuizBot, an AI assistant that creates professional quizzes.
        Your task is to generate exactly 10 multiple-choice questions from the provided YouTube transcript.
        Each question must:
        - Be clear, concise, and relevant to the transcript content
        - Include 4 answer options (A, B, C, D)
        - Clearly specify the correct answer
        Format the response strictly as structured data according to the schema provided.
        Do not include explanations, context, or additional text outside the schema.
        """

        # Build the reusable prompt
        self.quiz_prompt = self._build_prompt()

        # Structured LLM ensures output matches QuizList schema
        self.structured_llm = self.llm.with_structured_output(QuizList)

    def _build_prompt(self) -> ChatPromptTemplate:
        """
        Internal method to build the chat prompt for quiz generation.
        """
        user_template = """
        Here is the YouTube video transcript:
        {transcript}
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template(user_template),
        ])

    async def generate_quiz(self, transcript: str) -> QuizList:
        """
        Async method to generate a quiz from a transcript.
        """
        messages = self.quiz_prompt.format_prompt(transcript=transcript).to_messages()
        response = await self.structured_llm.ainvoke(messages)
        return response

# -------------------------
# Example usage (for testing)
# -------------------------
"""async def main():
    generator = QuizGenerator()
    transcript = load_transcript("https://youtu.be/p54vr-NyxDc")
    print("\n🎬 Loaded Transcript")
    if transcript:
        response = await generator.generate_quiz(transcript)
        print("\n📝 Generated Quiz:")
        for idx, quiz in enumerate(response.quizzes, 1):
            print(f"Q{idx}: {quiz.question}")
            print("Options:", quiz.options)
            print("Correct Answer:", quiz.correct_answer)
            print("Timestamp:", quiz.timestamp)
            print("--" * 20)
            
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())"""