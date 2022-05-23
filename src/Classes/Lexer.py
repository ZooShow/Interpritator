from src.Classes.Grammar import Grammar
import re

# 1 - индентефикатор
# 2 - оператор
# 3 - разделитель
# 4 - целое число
# 5 - число с точкой
# 6 - символ

class Lexer:
    textProgram = []
    grammar = Grammar
    lexems = []
    pointer = 0

    def __init__(self, grammar):
        self.grammar = grammar

    def read_file(self, filename):
        file = open(filename, 'r')
        separation = file.read().replace('\t', '')
        self.textProgram = re.sub(" +", " ", separation)

    def get_file(self):
        return self.textProgram

    def get_lexems(self):
        return self.lexems

    def get_next_symbol(self):
        temp_symbol = self.textProgram[self.pointer]
        self.pointer += 1
        return temp_symbol

    def skip_spaces(self, temp_symbol):
        if temp_symbol == ' ':
            next_symbol = self.get_next_symbol()
            return next_symbol
        return temp_symbol

    def is_identifer(self, word):
        if word in self.grammar.getIdnetifer():
            return True
        else:
            return False

    def is_separator(self, word):
        if word in self.grammar.getSeparator():
            return True
        else:
            return False

    def is_digit(self, word):
        try:
            float(word)
            return True
        except ValueError:
            return False

    def return_pointer(self):
        self.pointer -= 1

    def insert_identifer(self, word):
        self.grammar.insert_identifer(word)

    def print_lexemes(self):
        for item in self.lexems:
            print(item)

    def razbor(self):
        word = []
        while self.pointer != len(self.textProgram):
            char = self.get_next_symbol()
            # если буква
            if char.isalpha():
                word.append(char)
                char = self.get_next_symbol()
                while char.isalpha() or char.isdigit() or char == '_':
                    word.append(char)
                    char = self.get_next_symbol()
                self.return_pointer()
                tmp = ''.join(word)
                self.lexems.append([1, tmp])
                word.clear()
            # если цифра
            elif char.isdigit():
                word.append(char)
                char = self.get_next_symbol()
                type = 4
                while char.isdigit() or char == '.':
                    if char == '.':
                        type = 5
                    word.append(char)
                    char = self.get_next_symbol()
                self.return_pointer()
                tmp = ''.join(word)
                code = self.is_digit(tmp)
                if code:
                    self.lexems.append([type, tmp])
                else:
                    raise ValueError("NOT NUMBER")
                word.clear()
            elif char in ["-"]:
                next_char = self.get_next_symbol()
                if next_char.isdigit():
                    word.append(char)
                    word.append(next_char)
                    char = self.get_next_symbol()
                    type = 4
                    while char.isdigit() or char == '.':
                        if (char == '.'):
                            type = 5
                        word.append(char)
                        char = self.get_next_symbol()
                    self.return_pointer()
                    tmp = ''.join(word)
                    code = self.is_digit(tmp)
                    if code:
                        self.lexems.append([type, tmp])
                    else:
                        raise ValueError("NOT NUMBER")
                    word.clear()
                elif char == next_char:
                    self.lexems.append([2, char + char])
                else:
                    self.lexems.append([2, char])
                    self.return_pointer()

            # если логические операторы
            elif char == '|' or char == '&':
                next_char = self.get_next_symbol()
                if char == next_char:
                    self.lexems.append([2, char + char])
                else:
                    raise ValueError("Отсутсвует повторный символ ", char)
            # если арифметический оператор
            elif char in ['*', '%']:
                self.lexems.append([2, char])
            # если коммент или /
            elif char in ['/']:
                next_char = self.get_next_symbol()
                if char == next_char:
                    while char != '\n':
                        char = self.get_next_symbol()
                else:
                    self.lexems.append([2, char])
                self.return_pointer()
            elif char in ['+']:
                next_char = self.get_next_symbol()
                if char == next_char:
                    self.lexems.append([2, char + char])
                else:
                    self.lexems.append([2, char])
                    self.return_pointer()
            elif char in ['=', '!', '>', '<']:
                next_char = self.get_next_symbol()
                if next_char == '=':
                    self.lexems.append([2, char + '='])
                else:
                    self.lexems.append([2, char])
            # если разделитель
            elif char in self.grammar.getSeparator():
                self.lexems.append([3, char])
            elif char in ['\"']:
                word.append(char)
                char = self.get_next_symbol()
                length = len(self.textProgram)
                a = self.pointer + 1
                while not char in ["\"", '\n']:
                    word.append(char)
                    char = self.get_next_symbol()
                word.append(char)
                # self.return_pointer()
                if char == '\n':
                    raise ValueError("не закрыта кавычка")
                tmp = ''.join(word)
                word.clear()
                self.lexems.append([6, tmp])


