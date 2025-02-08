import json
import sys
from pathlib import Path

def validate_json_structure(data):
    """Validate the basic JSON structure and required fields."""
    if not isinstance(data, list):
        return False, "Root element must be an array"
    
    questions = {}
    choices = {}
    
    for item in data:
        if not isinstance(item, dict):
            return False, "Each item must be an object"
            
        required_fields = ["model", "pk", "fields"]
        for field in required_fields:
            if field not in item:
                return False, f"Missing required field: {field}"
                
        if item["model"] == "game.question":
            questions[item["pk"]] = {
                "mission": item["fields"]["mission"],
                "choices": []
            }
        elif item["model"] == "game.choice":
            question_id = item["fields"]["question"]
            if question_id not in questions:
                return False, f"Choice references non-existent question: {question_id}"
            questions[question_id]["choices"].append(item["pk"])
            choices[item["pk"]] = item["fields"]["is_correct"]
    
    # Validate that each question has exactly 3 choices
    for qid, qdata in questions.items():
        if len(qdata["choices"]) != 3:
            return False, f"Question {qid} has {len(qdata['choices'])} choices, expected 3"
        
        # Validate that each question has exactly one correct answer
        correct_answers = sum(1 for cid in qdata["choices"] if choices[cid])
        if correct_answers != 1:
            return False, f"Question {qid} has {correct_answers} correct answers, expected 1"
    
    # Validate that each mission has exactly 5 questions
    mission_questions = {}
    for qid, qdata in questions.items():
        mission = qdata["mission"]
        mission_questions[mission] = mission_questions.get(mission, 0) + 1
    
    for mission, count in mission_questions.items():
        if count != 5:
            return False, f"Mission {mission} has {count} questions, expected 5"
    
    return True, "Validation successful"

def main():
    fixture_path = Path(__file__).parent.parent / "fixtures" / "questions.json"
    
    try:
        with open(fixture_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {fixture_path}")
        sys.exit(1)
        
    is_valid, message = validate_json_structure(data)
    if not is_valid:
        print(f"Validation failed: {message}")
        sys.exit(1)
    else:
        print(message)
        sys.exit(0)

if __name__ == "__main__":
    main()