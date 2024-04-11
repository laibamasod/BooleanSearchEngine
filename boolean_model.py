from Stack import Stack
import numpy as np
import re

class BooleanModel:
    def __init__(self):
        # Initialize empty inverted index
        self.postings = {}

    def infix_to_postfix(self, tokens):
        """Converts an infix query into postfix"""

        stack = Stack()
        postfix = []

        for token in tokens:
            if self.is_left_bracket(token):
                stack.push(token)
            elif self.is_right_bracket(token):
                while not stack.is_empty() and stack.peek() != "(":
                    postfix.append(stack.pop())
                stack.pop()  # Discard the left bracket
            elif self.is_operator(token):
                while not stack.is_empty() and self.precedence(token) <= self.precedence(stack.peek()):
                    postfix.append(stack.pop())
                stack.push(token)
            else:
                postfix.append(token)

        while not stack.is_empty():
            postfix.append(stack.pop())

        return postfix

    def evaluate_query(self, query_tokens, inverted_index):
        operands = Stack()

        for token in query_tokens:
            if self.is_operator(token):
                right_operand = operands.pop()
                left_operand = operands.pop()
                result = self.__perform_operation(left_operand, right_operand, token)
                operands.push(result)
            else:
                token = self.__stem_token(token)
                operands.push(self.__bitvector(token, inverted_index))

        if len(operands) != 1:
            print("Malformed query or postfix expression")
            return []

        matching_docs = [i + 1 for i in np.where(operands.peek())[0]]
        return matching_docs

    def __stem_token(self, token):
        return token.lower()  # No stemming for now

    def __bitvector(self, word, inverted_index):
        doc_count = len(inverted_index)

        if word in inverted_index:
            bit_vector = np.zeros(doc_count, dtype=bool)
            posting = inverted_index[word]['documents']
            for doc_id in posting:
                doc_id = int(doc_id.strip())
                bit_vector[doc_id - 1] = True
            return bit_vector
        else:
            print(f"Warning: {word} was not found in the inverted index!")
            return np.zeros(doc_count, dtype=bool)

    def __perform_operation(self, left, right, op):
        if op == "&":
            return left & right
        elif op == "|":
            return left | right
        else:
            return 0

    def precedence(self, token):
        precedence = {"&": 2, "|": 1}
        return precedence.get(token, -1)

    def is_left_bracket(self, token):
        return token == "("

    def is_right_bracket(self, token):
        return token == ")"

    def is_operator(self, token):
        return token in {"&", "|"}

 
