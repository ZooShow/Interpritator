from src.Classes.Early.Earley import *

DOTRULE = "DOT"


class Node(object):
    def __init__(self, value, children, lexeme):
        self.state = value
        self.children = children
        self.lexeme = lexeme

    def __repr__(self):
        terms = [str(p) for p in self.state.production]
        terms.insert(self.state.dot_index, u"·")
        return "{0} -> {1}".format(self.state.name, " ".join(terms))


class Tree:
    def __init__(self, table, rules):
        self.table = table
        self.rules = rules
        self.tree = None
        self.file = None

    def build_tree(self):
        for state in self.table[-1]:
            if state.name == DOTRULE and state.completed():
                self.tree = self.reduce_node(self.table[0].states[0], len(self.table) - 1)
                return True
        else:
            print("Программа не верна")
            return False

    def reduce_node(self, state, j):
        terms = state.production
        k = len(terms) - 1
        c = j

        result = TreeNode(Rule(state.name, state.production), self.table[j].token)

        while k > -1:
            if isinstance(terms[k], Rule):
                nextStates = self.searchStates(state, k, c, state.startColumn)
                k -= 1
                if len(nextStates) > 0:
                    result.addChild(self.reduce_node(nextStates[-1], c))
                    c = nextStates[-1].startColumn.index
            else:
                k -= 1
                c -= 1
        return result

    def searchStates(self, inState, prodNum, columnNumber, i):
        subResult = []
        for state in self.table[columnNumber].states:
            if state.name == inState.production[prodNum].name and state.completed() and state != inState:
                subResult.append(state)

        result = []
        for state in subResult:
            if self.search_states_helper(state.name, state.startColumn, i):
                result.append(state)

        return result

    def search_states_helper(self, x, column, i):
        for state in column.states:
            if not state.completed() and \
                    isinstance(state.production[state.dot_index], Rule) and \
                    state.production[state.dot_index].name == x and \
                    state.startColumn == i:
                return True

        return False

    def print_tree_to_file(self, filename):
        if self.tree is not None:
            with open(filename, "w+", encoding="utf-8") as file:
                self.file = file
                self.sub_tree_print(self.tree)

    def sub_tree_print(self, current_node, indent='', nodeType='init'):
        if current_node.lexeme is None:
            name = ''
        else:
            name = current_node.lexeme[1]
        name = repr(current_node.rule) + name

        if nodeType == 'last':
            start_shape = "\\" + "-" * 4
        elif nodeType == 'mid':
            start_shape = "\t" + "-" * 4
        else:
            start_shape = ' '

        line = '{0}{1}{2}'.format(indent, start_shape, name)
        self.file.write(line + '\n')
        nextIndent = '{0}{1}'.format(
            indent,
            "|" + ' ' * (len(start_shape))
            if nodeType == 'mid' else ' ' * (len(start_shape) + 1))

        if len(current_node.children) != 0:
            if len(current_node.children) == 1:
                self.sub_tree_print(current_node.children[0], nextIndent, 'last')
            else:
                for i in range(0, len(current_node.children) - 1):
                    self.sub_tree_print(current_node.children[i], nextIndent, 'mid')

                self.sub_tree_print(current_node.children[-1], nextIndent, 'last')
