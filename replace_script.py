import re
import sys

with open('backend/services/placement_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''def generate_mock_module(module_key: str, topic: str | None, difficulty: str, count: int = 20, user_id: str = None) -> dict[str, Any]:
    topic = topic or random.choice(APPLIED_TOPICS.get(module_key, [module_key.title()]))
    questions = generate_question_set(module_key, topic, difficulty, count=count, user_id=user_id)
    return {
        \"module\": module_key,
        \"topic\": topic,
        \"difficulty\": difficulty,
        \"questions\": questions,
    }'''

new_func = '''def generate_mock_module(module_key: str, topic: str | None, difficulty: str, count: int = 20, user_id: str = None) -> dict[str, Any]:
    topic = topic or random.choice(APPLIED_TOPICS.get(module_key, [module_key.title()]))
    
    easy_count = int(count * 0.35)
    hard_count = int(count * 0.25)
    medium_count = count - easy_count - hard_count
    
    q_easy = generate_question_set(module_key, topic, "easy", count=easy_count, user_id=user_id)
    q_medium = generate_question_set(module_key, topic, "medium", count=medium_count, user_id=user_id)
    q_hard = generate_question_set(module_key, topic, "hard", count=hard_count, user_id=user_id)
    
    questions = q_easy + q_medium + q_hard
    random.shuffle(questions)
    
    for idx, q in enumerate(questions):
        q["order"] = idx + 1

    return {
        \"module\": module_key,
        \"topic\": topic,
        \"difficulty\": \"Mixed\",
        \"questions\": questions,
    }'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('backend/services/placement_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Successfully replaced generate_mock_module!')
else:
    print('Failed to find exact block.')
