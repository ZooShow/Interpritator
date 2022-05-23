from src.Classes.Early.Tree import Node
from src.Classes.Grammar import *


class Variable(object):
    def __init__(self, type_v, name):
        self.type_v = type_v
        self.name = name
        self.is_use = False


class Function(object):
    def __init__(self, security_modifier=None, type_v=None, name=None):
        self.security_modifier = security_modifier
        self.type_v = type_v
        self.name = name
        self.params = []
        self.is_used_in_main = False


class Storage(object):
    def __init__(self, name):
        self.variables = list()
        self.functions = list()
        self.children = list()
        self.parent = None
        self.name = name

    def add_dop_scope(self, name):
        var_s = Storage(name)
        self.children.append(var_s)
        var_s.parent = self
        return var_s

    def add_variable(self, var: Variable):
        self.variables.append(var)

    def add_function(self, var: Function):
        self.functions.append(var)

    def is_exist_variable(self, name, scope):
        while scope is not None:
            for value in scope.variables:
                if value.name == name:
                    value.is_use = True
                    return True
            scope = scope.parent
        return False

    def is_exist_function(self, name, scope):
        while scope.name != 'class':
            scope = scope.parent
        for child in scope.children:
            fun_in_child = child.functions
            for function in fun_in_child:
                if function.name == name:
                    return True
        return False

    def get_variable(self, name, scope):
        while scope is not None:
            for value in scope.variables:
                if value.name[1] == name:
                    value.is_use = True
                    return value
            scope = scope.parent
        return None

    def getFunction(self, name, scope):
        while scope.name != 'class':
            scope = scope.parent
        while scope is not None:
            for child in scope.children:
                for value in child.functions:
                    if value.name == name:
                        return value
                scope = scope.parent
        return None


class SemanticError:
    def __init__(self, name, error_name):
        self.errorName = error_name
        self.name = name

    def __str__(self):
        return "Ошибка: {1}{0}" \
            .format(self.errorName, self.name)


class VariableSemanticAnalyser:
    def __init__(self, tree, grammar: Grammar, count_error = 0):
        self.tree = tree
        self.functions = []
        self.file = None
        self.grammar = grammar
        self.count_error = count_error

    def find_expression_type(self, node: Node, scope):
        if node.lexeme and node.lexeme[0] == 4:
            return ['int']
        if node.lexeme and node.lexeme[0] == 5:
            return ['double']
        if node.lexeme and node.lexeme in self.grammar.symbol:
            return ['string']
        if node.lexeme and node.lexeme[1] in ['true', 'false']:
            return ['boolean']
        if node.lexeme and node.lexeme[0] == 3:
            tmp = self.get_func(node.children)
            type = scope.getFunction(tmp[0].children[0].lexeme[1], scope)
            if type is None:
                print(
                    SemanticError(
                        tmp[0].children[0].lexeme[1],
                        ": нельзя вызвать процедуру"
                    )
                )
                self.count_error += 1
                return
            type.is_used_in_main = True
            count_par = self.check_count_of_param(type)
            if count_par > 0:
                if len(tmp[0].children) == 1:
                    params = 0
                else:
                    params = self.get_params_in_main(tmp[0].children[1], scope)
                    if params is None:
                        return
                if len(params) != count_par:
                    print(
                        SemanticError(
                            type.name,
                            ': неверное количество передаваемых параметров'
                        )
                    )
                    self.count_error += 1
                if not self.inspect_param(self.get_par_fun(type), params):
                    print(
                        SemanticError(
                            type.name,
                            ': не верный тип одного из передаваемых значений'
                        )
                    )
                    self.count_error += 1
                    return
            return [type.type_v]
        else:
            variable = scope.get_variable(node.lexeme[1], scope)
            if variable is None:
                print(
                    SemanticError(
                        node.lexeme[1], ": переменная не объявлена"
                    )
                )
                self.count_error += 1
                return
            return [variable.type_v[1]]

    def inspect_param(self, mas1, mas2):
        for i in range(0, len(mas1), 1):
            if mas1[i] != mas2[i]:
                return False
        return True

    def get_par_fun(self, node):
        tmp = []
        for param in node.params:
            tmp.append(param.type_v[1])
        return tmp

    def get_params_in_main(self, node: TreeNode, scope):
        tmp = []
        children = node.children
        while len(children) != 1:
            type = self.get_type(children, scope)
            if type is None:
                return
            tmp.append(type)
            children = children[1].children
        tmp.append(self.get_type(children, scope))
        return tmp

    def get_type(self, children, scope):
        if children[0].lexeme[1] in ['true', 'false']:
            return 'boolean'
        elif children[0].lexeme[0] == 1:
            var = scope.get_variable(children[0].lexeme[1], scope)
            if var is None:
                print(
                    SemanticError(
                        children[0].lexeme[1],
                        ': переменная не определена'
                    )
                )
                self.count_error += 1
                return
            return var.type_v[1]
        elif children[0].lexeme[0] == 4:
            return 'int'
        elif children[0].lexeme[0] == 5:
            return 'double'

    def check_count_of_param(self, f: Function):
        return len(f.params)

    def get_func(self, node: Node):
        while node[0].children is not None and node[0].rule.name != '<вызов функции>':
            node = node[0].children
        return node

    def add_variable(self, node: Node, scope: Storage):
        newVariable = Variable(None, None)
        typeCheck = None
        errorCheck = None
        for part in node.children:
            if part.rule.name == '<тип данных>':
                newVariable.type_v = part.lexeme
            if part.rule.name == '<имя переменной>':
                newVariable.name = part.lexeme
            if part.rule.name == '<выражение>':
                typeCheck = self.find_expression_type(part, scope)
        if typeCheck and newVariable.type_v[1] not in typeCheck and newVariable.name[1] is not None:
            print(
                SemanticError(
                    newVariable.name[1],
                    ": неверный тип данных"
                )
            )
            self.count_error += 1
            errorCheck = True
        if newVariable.name in self.grammar.getIdnetifer() and newVariable.name[0] is not None:
            print(
                SemanticError(
                    newVariable.name,
                    ": зарезервированное слово")
            )
            self.count_error += 1
            errorCheck = True
        if scope.is_exist_variable(newVariable.name, scope):
            print(
                SemanticError(
                    newVariable.name[1],
                    ": имя переменной уже используется"
                )
            )
            self.count_error += 1
            errorCheck = True
        if errorCheck is None:
            scope.add_variable(newVariable)

    def update_variable(self, node: Node, scope: Storage):
        typeCheck = None
        nameCheck = ''
        for part in node.children:
            if part.rule.name == '<имя переменной>':
                nameCheck = part.lexeme
            if part.rule.name == '<выражение>':
                typeCheck = self.find_expression_type(part, scope)
            if part.rule.name == '<унарный алгебраический оператор>':
                typeCheck = ['int']
        if not scope.is_exist_variable(nameCheck, scope):
            print(
                SemanticError(
                    nameCheck[1],
                    ": переменная не объявлена"
                    )
            )
            self.count_error += 1
        else:
            var = scope.get_variable(nameCheck[1], scope)
            if var.type_v[1] not in typeCheck:
                print(
                    SemanticError(
                        nameCheck[1],
                        ": не верный тип данных"
                    )
                )
                self.count_error += 1

    def add_function(self, node: Node, scope: Storage):
        newFunction = Function()
        for part in node.children:
            if part.rule.name == '<модификатор доступа>':
                newFunction.security_modifier = part.lexeme[1]
            if part.rule.name == '<тип данных>':
                newFunction.type_v = part.lexeme[1]
            if part.rule.name == '<имя переменной>':
                newFunction.name = part.lexeme[1]
            if part.rule.name == '<формальные параметры>':
                children = part.children
                while len(children) != 1:
                    var = Variable(children[0].children[0].lexeme, children[0].lexeme)
                    scope.add_variable(var)
                    newFunction.params.append(var)
                    children = children[1].children
                var = Variable(children[0].children[0].lexeme, children[0].lexeme)
                scope.add_variable(var)
                newFunction.params.append(var)
            if part.rule.name == '<тело функции>':
                self.parse(part, scope)
                returnExpression = part.children
                while len(returnExpression) != 1:
                    returnExpression = returnExpression[1].children
                returnExpression = self.parse_exp(returnExpression[0].children[0].children[0], scope)
                if newFunction.type_v in returnExpression:
                    if scope.is_exist_function(newFunction.name, scope):
                        print(
                            SemanticError(
                                newFunction.name,
                                ': данное имя функции уже существует'
                            )
                        )
                        self.count_error += 1
                        return
                    self.functions.append(newFunction)
                elif len(returnExpression) == 0:
                    print(
                        SemanticError(
                            newFunction.name, ": проблема в возвращаемом типе"
                        )
                    )
                    self.count_error += 1
                else:
                    print(
                        SemanticError(
                            newFunction.name,
                            ": неверный тип возвращаемых данных в функции")
                    )
                    self.count_error += 1
        scope.add_function(newFunction)

    def parse_exp(self, expression, scope: Storage):
        rule_name = expression.rule.name
        if rule_name == '<булево выражение>' or '<алгебраическое выражение>':
            if len(expression.children) == 1:
                return self.parse_operand(expression.children[0], scope)
            if expression.children[0].rule.name == '<унарный алгебраический оператор>':
                return [self.parse_operand(expression.children[1], scope)]
            if expression.children[1].rule.name == '<бинарный алгебраический оператор>':
                return [self.parse_double_operand(expression, scope)]
            else:
                exp_type = self.parse_operand(expression.children[0], scope)
                expression_temp = expression.children[2]
                while len(expression_temp.children) == 3:
                    if exp_type != self.parse_operand(expression_temp.children[0], scope):
                        return []
                    expression_temp = expression_temp.children[2]
                if exp_type != self.parse_operand(expression_temp.children[0], scope):
                    return []
                return [exp_type]

    def parse_double_operand(self, operand: TreeNode, scope: Storage):
        if operand.lexeme[0] == 4:
            type = 'int'
        if operand.lexeme[0] == 5:
            type = 'double'
        if operand.lexeme[0] == 1:
            type = scope.get_variable(operand.lexeme[1], scope)
            if type is None:
                print(
                    SemanticError(
                        operand.lexeme[1],
                        ": переменная не объявлена"
                    )
                )
                self.count_error += 1
                return
            type = type.type_v[1]
        for i in range(0, len(operand.children), 2):
            if operand.children[i].rule.name == '<алгебраический операнд>':
                type_op = self.find_expression_type(operand.children[i], scope)[0]
                if type_op != type:
                    return
            else:
                type_op = self.parse_double_operand(operand.children[i], scope)
                if type_op != type:
                    return
        return type

    def parse_operand(self, operand: TreeNode, scope: Storage):
        rule_name = operand.children[0].rule.name
        if rule_name == '<имя переменной>':
            type = scope.get_variable(operand.children[0].lexeme[1], scope)
            if type is None:
                return []
            return type.type_v[1]
        if rule_name == '<вызов функции>':
            for func in self.functions:
                if func.name == operand.children[0].children[0].lexeme:
                    return func.type_v
            return None
        if rule_name == '<число>':
            if operand.lexeme[0] == 4:
                return ['int']
            if operand.lexeme[0] == 5:
                return ['double']

    def parse(self, node, scope: Storage):
        new_scope = scope
        if node.rule.name == '<инициализация переменной>' and scope.name != 'func':
            self.add_variable(node, scope)
        if node.rule.name == '<объявление переменной>':
            self.add_variable(node, scope)
        # if node.rule.name == '<вызов функции>':

        if node.rule.name == '<обновление переменной>':
            self.update_variable(node, scope)
        if node.rule.name == '<цикл for>':
            new_scope = scope.add_dop_scope('for')
        if node.rule.name == '<цикл while>':
            new_scope = scope.add_dop_scope('while')
        if node.rule.name == '<главная процедура>':
            new_scope = scope.add_dop_scope('main procedure')
        if node.rule.name == '<объявление класса>':
            new_scope = scope.add_dop_scope('class')
        if node.children:
            for nextNode in node.children:
                if nextNode.rule.name in ['<объявление функции>', '<объявление процедуры>']:
                    new_scope = scope.add_dop_scope('func')
                    self.add_function(nextNode, new_scope)
                if nextNode.rule.name == '<функции>':
                    self.parse(nextNode, scope)
                else:
                    self.parse(nextNode, new_scope)

    def get_non_use_func(self, scope):
        tmp = []
        scopes = scope.children[0].children
        for child in scopes:
            fun_in_child = child.functions
            for function in fun_in_child:
                if not function.is_used_in_main:
                    tmp.append(function.name)
        return tmp

    def get_use_variable(self, scope):
        tmp = []
        for child in scope.children:
            variables = child.variables
            for variable in variables:
                if not variable.is_use:
                    tmp.append(variable.name)
        return tmp
