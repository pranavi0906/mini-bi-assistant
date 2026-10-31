from app.gemini_interpreter import interpret_with_gemini


questions = [
    "What is our total revenue?",
    "Which product made us the most money?",
    "Did sales improve in February compared with January?",
    "How many products did we sell?",
    "What is the weather today?",
]

for question in questions:
    print("\nQuestion:", question)

    try:
        result = interpret_with_gemini(question)
        print("Gemini interpretation:", result)

    except Exception as error:
        print("Error:", error)