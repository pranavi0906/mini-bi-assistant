# AI Development Notes

## 1. AI Tools Used

- **Google Gemini API:** Used for interpreting natural-language business questions and mapping them to supported analytics intents.
- **ChatGPT:** Used as a development assistant for implementation guidance, code review, debugging support, and documentation preparation.

## 2. How AI Was Used During Development

AI assistance was used to understand the project requirements, design the application workflow, implement and refine the question interpretation logic, and troubleshoot integration issues.

Gemini was integrated into the application to interpret user questions. The identified intent is then handled by the analytics layer, which executes SQL queries against the SQLite database.

ChatGPT was used to assist with debugging, understanding errors, improving code, and preparing project documentation.

## 3. Problems Encountered

- Mapping different natural-language questions to the correct analytics intent.
- Handling unsupported or ambiguous questions.
- Integrating the Gemini API with the FastAPI backend.
- Handling database query results with the correct column names and data types.
- Ensuring that revenue calculations use only valid completed transactions.
- Testing the backend and frontend integration.

## 4. How the Problems Were Debugged

The application logs and API responses were used to identify errors.

For example, while implementing the product-listing feature, the API initially returned a 500 Internal Server Error because the database query results were accessed using an incorrect key.

The returned database row was inspected, revealing that the result was a dictionary with a lowercase `product` key. The extraction logic was corrected accordingly.

Automated tests were also used to validate the analytics calculations.

## 5. Improvements With Another Day of Work

With another day of development, I would:

- Improve the handling of ambiguous and unsupported questions.
- Add more test cases for natural-language interpretation.
- Add interactive charts for monthly and category-wise analytics.
- Improve the frontend presentation of results.
- Add more business metrics and support for additional datasets.
- Improve error handling and validation across the application.