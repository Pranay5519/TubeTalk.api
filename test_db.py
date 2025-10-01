from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.crud import load_quiz_from_db  # assuming you saved the function

# Create a database session
db: Session = SessionLocal()

# Load quiz for a specific thread_id
thread_id = "roadmap"
quiz_list = load_quiz_from_db(db, thread_id)

if quiz_list:
    print(quiz_list)
else:
    print("No quiz found for this thread_id.")

# Close the session
db.close()
