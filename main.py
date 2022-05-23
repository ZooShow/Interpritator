import sys
from src.Classes.CodeGen import CodeGen
from src.Classes.Early.Earley import *
from src.Classes.Early.Tree import Tree
from src.Classes.Grammar import Grammar
from src.Classes.Lexer import Lexer
from src.Classes.Optimizer import Optimizer
from src.Classes.Semantic import Storage, VariableSemanticAnalyser

if __name__ == '__main__':
    sys.setrecursionlimit(2500)

    grammar = Grammar()
    grammar.setDigit(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
    grammar.setSeparator(grammar.read_file("src/Grammar/separator.txt"))
    grammar.setIdnetifer(grammar.read_file("src/Grammar/identifer.txt"))
    grammar.setRule("src/Grammar/rule.json")

    lexer = Lexer(grammar)
    lexer.read_file('input.txt')
    lexer.razbor()

    early = Earley(grammar.rules, "<программа>")
    early_result = early.parse(lexer.lexems)
    early.print_table_to_file('table.txt')

    if early_result:
        treeBuilder = Tree(early.table, grammar.rules)
        treeBuilder.build_tree()
        treeBuilder.print_tree_to_file('tree.txt')

        variable = Storage('program')
        semantic_analyzer = VariableSemanticAnalyser(treeBuilder.tree, grammar)
        semantic_problems = semantic_analyzer.parse(treeBuilder.tree, variable)
        count_of_semantic_problems = semantic_analyzer.count_error
        if count_of_semantic_problems == 0:
            code_gen = CodeGen()
            code_gen.printTreeToFile(early.table, 'output.txt', grammar)

            optimizer = Optimizer()
            non_use_fun = semantic_analyzer.get_non_use_func(variable)
            newTable = optimizer.delete_non_use_fun(early.table, non_use_fun)
            code_gen.printTreeToFile(newTable, 'outputOptimize.txt', grammar)
            print('Успешно интерпретировано!')
    else:
        print('Программа написана не корректно!')
