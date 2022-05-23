class Optimizer:
    def delete_non_use_fun(self, table, none_use_fun):
        tmp = table
        for fun_name in none_use_fun:
            tmp = self.delete_non_use_fun_helper(tmp, fun_name)
        return tmp

    def delete_non_use_fun_helper(self, table, name):
        i = 1
        length = len(table)
        while i < length:
            if table[i].token[1] == name:
                if table[i - 2].token[1] == 'static':
                    start = i - 3
                    while not (table[i].states[0].name in ['<объявление функции>', '<объявление процедуры>'] and table[i].token[1] == '}'):
                        i += 1
                    end = i
                    del (table[start:end + 1])
                    return table
            i += 1
        return table

    def collapse_digit(self, table):
        i = 1
        length = len(table)
        while i < length:
            if table[i].token[0] in [4, 5]:
                start = i
                str = ''
                while table[i].token[1] != ';':
                    if table[i].token[0] in [1, 2, 3, 4, 5]:
                        str += table[i].token[1]
                    i += 1
                end = i
            i += 1
        return str

