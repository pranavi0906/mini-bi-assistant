from app.question_interpreter import answer_question

questions = [
    "What is our total revenue?",
    "Which product made us the most money?",
    "Did February outperform January?",
    "How many units did we sell?",
    "What is the weather today?",
]

for question in questions:
    print("\nQuestion:", question)
    print("Answer:", answer_question(question))