from pydantic import BaseModel, Field
from typing import List


class Quiz(BaseModel):
    question: str = Field(description="A well-formed multiple-choice quiz question")
    options: List[str] = Field(description="List of 4 possible answer options")
    correct_answer: str = Field(description="The correct answer from the options list")
    timestamp : float = Field(description="timestamp from where the quesiton was picked from the transcripts")
class QuizList(BaseModel):
    quizzes: List[Quiz] = Field(description="List of 10 quiz questions with options and answers")
