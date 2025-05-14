# tokenising (lexical analysis phase)
import re

# Token specs
token_specs = [
    ('INT',       r'int'),
    ('IF',        r'if'),
    ('ELSE',      r'else'),
    ('WHILE',     r'while'),
    ('FOR',       r'for'),
    ('PRINT',     r'print'),
    ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUM',       r'\d+'),
    ('GE',        r'>='),
    ('LE',        r'<='),
    ('EQ',        r'=='),
    ('GT',        r'>'),
    ('LT',        r'<'),
    ('ASSIGN',    r'='),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('MULT',      r'\*'),
    ('DIV',       r'/'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('SEMICOLON', r';'),
    ('WHITESPACE', r'\s+'),
]

# Combine into one regex
token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)

def tokenize(code):
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'WHITESPACE':
            continue  # skip spaces
        tokens.append((kind, value))
    return tokens

code = '''
int i;
int sum;
i = 0;
sum = 0;
for (i = 0; i < 5; i = i + 1;) {
sum = sum + i;
}
print(sum)

'''

# int x;
# int y;
# x = 5;
# y = 10;

# if (x < y) {
#     print(x)
# } else {
#     print(y)
# }

# for (x = 0; x < 5; x = x + 1;) {
#     print(x)
# }

# int a;
# a = 7;
# if (a < 2) {
#   print(a)  
# } else {
#   a = a + 1;
#   print(a)  
# }


# ''' if (a<0) {
#     print("Negative number") // Negative number
# } else{
#     print("Positive number") // Positive number
# }'''
# int i;
# int sum;
# i = 0;
# sum = 0;
# for (i = 0; i < 5; i = i + 1;) {
#   sum = sum + i;
# }
# print(sum)


# int y;
# y = 0;
# while (y < 5) {
#   y = y + 1;
# }
# print(y)


# int x;
# x = 5;
# if (x > 3) {
#   x = x + 1;
# }

# int x;
# x = 5 + 3;
# if (x > 2) {
#     print(x)
# }

# int x;
# int y;
# int z;
# x=5;
# y=3;
# z=x+y;
# print(z)

for token in tokenize(code):
    print(token)
