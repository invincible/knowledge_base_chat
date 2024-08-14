from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz
from models import Question, Answer, DecisionTree, TreeNode


def get_closest_answer(db: Session, user_input: str):
    questions = db.query(Question).all()
    best_match = None
    highest_score = 0

    for question in questions:
        score = max(fuzz.ratio(user_input.lower(), question.question.lower()),
                    fuzz.ratio(user_input.lower(), question.keywords.lower()))
        if score > highest_score:
            highest_score = score
            best_match = question

    if best_match and highest_score > 70:  # Пороговое значение
        return db.query(Answer).filter(Answer.question_id == best_match.id).first()

    return None


def format_response(answer: Answer):
    if not answer:
        return "Ответ не найден, можно отправить запрос на специалиста"

    response = answer.answer_text
    buttons = answer.buttons.split(',') if answer.buttons else []
    spoiler = answer.spoiler
    table = answer.table_data

    return response, buttons, spoiler, table


def get_next_node(db: Session, tree_id: int, node_id: int, user_input: str):
    current_node = db.query(TreeNode).filter(TreeNode.id == node_id).first()
    if not current_node:
        return None

    for child in current_node.children:
        if fuzz.ratio(user_input.lower(), child.question.lower()) > 70:
            return child

    return None


def check_for_decision_tree(db: Session, user_input: str):
    trees = db.query(DecisionTree).all()
    for tree in trees:
        root_node = db.query(TreeNode).filter(TreeNode.tree_id == tree.id, TreeNode.parent_id == None).first()
        if root_node and fuzz.ratio(user_input.lower(), root_node.question.lower()) > 70:
            return {"id": tree.id, "root_node_id": root_node.id}
    return None


def process_user_input(db: Session, user_input: str, context: dict):
    if context.get('current_tree'):
        next_node = get_next_node(db, context['current_tree'], context['current_node'], user_input)
        if next_node:
            context['current_node'] = next_node.id
            return next_node.answer, context
        else:
            context.pop('current_tree')
            context.pop('current_node')

    answer = get_closest_answer(db, user_input)
    if answer:
        return format_response(answer), context

    tree = check_for_decision_tree(db, user_input)
    if tree:
        context['current_tree'] = tree['id']
        context['current_node'] = tree['root_node_id']
        root_node = db.query(TreeNode).filter(TreeNode.id == tree['root_node_id']).first()
        return root_node.question, context

    return "Извините, я не могу найти подходящий ответ.", context