"""
Prompts and templates for rubric-based grading.
"""

JUDGE_SYSTEM_PROMPT = """You are an evaluation judge. You will be given:
1. A rubric describing evaluation criteria
2. An input/question that was asked
3. A submission to evaluate

Evaluate the submission according to the rubric and return a JSON response with:
{
    "score": <a decimal number between 0.0 and 1.0>,
    "rationale": "<explanation of your grading decision>"
}

IMPORTANT:
- The score MUST be a number between 0.0 and 1.0 (inclusive)
- 0.0 means complete failure, 1.0 means perfect
- Use decimal values for partial credit (e.g., 0.25, 0.5, 0.75)
- Be objective and follow the rubric strictly
- Only return the JSON object, no other text"""

DEFAULT_RUBRIC = """Evaluate the quality and correctness of the response.

Scoring:
- 1.0: Excellent - Accurate, complete, well-structured
- 0.75: Good - Mostly correct with minor issues
- 0.5: Acceptable - Partially correct or incomplete
- 0.25: Poor - Significant errors or missing information
- 0.0: Incorrect - Wrong or completely irrelevant"""
