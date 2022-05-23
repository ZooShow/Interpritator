import re

DOTRULE = "DOT"


class TreeNode(object):
    def __init__(self, rule, lexeme):
        self.rule = rule
        self.lexeme = lexeme
        self.children = []

    def __repr__(self):
        return str(self.rule)

    def addChild(self, child):
        self.children = [child] + self.children


class Production(object):
    def __init__(self, *terms):
        self.terms = terms

    def __len__(self):
        return len(self.terms)

    def __getitem__(self, index):
        return self.terms[index]

    def __iter__(self):
        return iter(self.terms)

    def __repr__(self):
        return " ".join(str(t) for t in self.terms)

    def __eq__(self, other):
        if not isinstance(other, Production):
            return False
        return self.terms == other.terms

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.terms)

    def add(self, term):
        self.terms += (term,)


class Rule(object):
    def __init__(self, name, *productions: Production):
        self.name = name
        self.productions = list(productions)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s -> %s" % (self.name, " | ".join(repr(p) for p in self.productions))

    def add(self, *productions):
        self.productions.extend(productions)


class RegexpRule(object):
    def __init__(self, regexp):
        self.regexp = regexp

    def __repr__(self):
        return self.regexp

    def __str__(self):
        return self.regexp


class State(object):
    def __init__(self, name, production, dotIndex, startColumn):
        self.name = name
        self.production = production
        self.startColumn = startColumn
        self.end_column = None
        self.dot_index = dotIndex
        self.rules = [t for t in production if isinstance(t, Rule)]
        self.children = []

    def __repr__(self):
        terms = [str(p) for p in self.production]
        terms.insert(self.dot_index, u"·")
        return "%-5s -> %-16s [%s-%s]" % (self.name, " ".join(terms), self.startColumn, self.end_column)

    def __eq__(self, other):
        return (self.name, self.production, self.dot_index, self.startColumn) == \
               (other.name, other.production, other.dot_index, other.startColumn)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.name, self.production))

    def __len__(self):
        return len(str(self))

    def completed(self):
        return self.dot_index >= len(self.production)

    def next_term(self):
        if self.completed():
            return None
        return self.production[self.dot_index]

    def addChild(self, state):
        self.children.append(state)


class Column(object):
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.states = []
        self._unique = set()

    def __str__(self):
        return str(self.index)

    def __len__(self):
        return len(self.states)

    def __iter__(self):
        return iter(self.states)

    def __getitem__(self, index):
        return self.states[index]

    def add(self, state):
        if state not in self._unique:
            self._unique.add(state)
            state.end_column = self
            self.states.append(state)
            return True
        return False


class Earley:
    def __init__(self, rules, axiom):
        self.rules = rules
        self.axiom = None
        self.table = None

        for rule in rules:
            if rule.name == axiom:
                self.axiom = rule

        if self.axiom is None:
            raise ValueError("Invalid axiom")

    def guess(self, col, rule, state):
        for prod in rule.productions:
            newState = State(rule.name, prod, 0, col)
            col.add(newState)
            state.addChild(newState)

    def check(self, col, state, token):
        if not isinstance(token, RegexpRule):
            if token == col.token[1]:
                col.add(State(state.name, state.production, state.dot_index + 1, state.startColumn))
                state.addChild(col[-1])
        else:
            match = re.search(token.regexp, col.token[1])
            if match:
                col.add(State(state.name, state.production, state.dot_index + 1, state.startColumn))
                state.addChild(col[-1])

    def complete(self, col, state):
        if not state.completed():
            return
        for st in state.startColumn:
            term = st.next_term()
            if not isinstance(term, Rule):
                continue
            if term.name == state.name:
                col.add(State(st.name, st.production, st.dot_index + 1, st.startColumn))
                st.addChild(col[-1])

    def parse(self, lexemeArray):
        self.table = [Column(i, tok) for i, tok in enumerate([None] + lexemeArray)]
        self.table[0].add(State(DOTRULE, Production(self.axiom), 0, self.table[0]))

        for i, col in enumerate(self.table):
            for state in col:
                if state.completed():
                    self.complete(col, state)
                else:
                    term = state.next_term()
                    if isinstance(term, Rule):
                        self.guess(col, term, state)
                    elif i + 1 < len(self.table):
                        self.check(self.table[i + 1], state, term)

        for st in self.table[-1]:
            if st.name == DOTRULE and st.completed():
                return True
        else:
            return False

    def print_table_to_file(self, filename):
        with open(filename, "w+", encoding="utf-8") as file:
            i = 0
            for col in self.table:
                file.write('State ' + str(i) + '\n')
                for state in col.states:
                    file.write(str(state))
                i += 1
                file.write("\n")

