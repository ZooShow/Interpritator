import json
import re

from src.Classes.Early.Earley import *

class Grammar:
    def __init__(self):
        self.identifer = []
        self.separator = []
        self.digit = []
        self.symbol = []
        self.rules = []

    def insert_identifer(self, word):
        self.identifer.append(word)

    def read_file(self, filename):
        file = open(filename, 'r')
        return file.read().split('\n')

    def setIdnetifer(self, identifer):
        self.identifer = identifer

    def setSeparator(self, separator):
        self.separator = separator

    def setDigit(self, digit):
        self.digit = digit

    def setSymbol(self, symbol):
        self.symbol = symbol

    def getIdnetifer(self):
        return self.identifer

    def getSeparator(self):
        return self.separator

    def getDigit(self):
        return self.digit

    def getSymbol(self):
        return self.symbol

    def getRule(self, ruleName):
        for rule in self.rules:
            if rule.name == ruleName:
                return rule
        return None

    def setRule(self, filename):
        with open(filename, 'r', encoding="utf-8") as jsonFile:
            src = json.load(jsonFile)

            for i, rule in enumerate(src):
                rule = rule['name']
                if self.getRule(rule) is None:
                    self.rules.append(Rule(rule))

            for i, rule in enumerate(src):
                current = self.getRule(rule['name'])
                conditions = rule['conditions']
                for condition in conditions:
                    acc = Production()
                    for item in condition:
                        existRule = self.getRule(item)
                        if existRule:
                            acc.add(existRule)
                        else:
                            match = re.search('reg{(.+)}', item)
                            if match:
                                acc.add(RegexpRule(match.group(1)))
                            else:
                                acc.add(item)
                    current.add(acc)

