from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    keywords = Column(String, nullable=False)
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_text = Column(String, nullable=False)
    buttons = Column(String)
    spoiler = Column(String)
    table_data = Column(String)
    question = relationship("Question", back_populates="answers")


class DecisionTree(Base):
    __tablename__ = 'decision_trees'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    nodes = relationship("TreeNode", back_populates="tree")


class TreeNode(Base):
    __tablename__ = 'tree_nodes'

    id = Column(Integer, primary_key=True)
    tree_id = Column(Integer, ForeignKey('decision_trees.id'))
    parent_id = Column(Integer, ForeignKey('tree_nodes.id'))
    question = Column(String)
    answer = Column(String)
    tree = relationship("DecisionTree", back_populates="nodes")
    parent = relationship("TreeNode", remote_side=[id])
    children = relationship("TreeNode")