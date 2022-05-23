class CodeGen:
    def printTreeToFile(self, table, filename, grammar):
        with open(filename, "w+", encoding="utf-8") as file:
            file.write('using System; \n')
            i = 1
            length = len(table)
            tab = 0
            while i < length:
                if table[i].token[1] == ';':
                    file.write('; \n' + ' ' * tab)
                elif table[i].token[1] == '{':
                    tab += 2
                    file.write(' { \n' + ' ' * tab)
                elif table[i].token[1] == '}':
                    tab -= 2
                    file.write(' ' * tab + '} \n')
                elif table[i].token[1] == 'boolean':
                    file.write('bool ')
                elif table[i].token[1] == 'System':
                    file.write(' ' * tab + 'Console')
                    file.write(table[i+1].token[1])
                    i += 3
                elif table[i].token[1] == 'println':
                    file.write('WriteLine')
                elif table[i].token[1] in grammar.separator:
                    file.write(table[i].token[1])
                elif table[i].token[1] == 'main':
                    file.write('Main')
                elif table[i].token[1] == 'class':
                    file.write(table[i].token[1] + ' ')
                    file.write(table[i+1].token[1].lower())
                    i += 1
                else:
                    file.write(table[i].token[1] + ' ')
                i += 1
