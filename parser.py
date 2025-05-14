from semantic_checker import SemanticAnalyzer  # Import the semantic analyzer

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # List of tokens
        self.pos = 0  # Current position in token list
        self.semantic = SemanticAnalyzer()  # Add semantic analyzer
        self.intermediate_code = []     
        self.temp_count = 0
        self.label_count = 0
    # To store three-address code (TAC)
        
    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label



    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None  # End of input

    def consume(self):
        """Advance to the next token."""
        self.pos += 1

    def match(self, token_type):
        """Consume the current token if it matches the expected type."""
        if self.current_token() and self.current_token()[0] == token_type:
            self.consume()
        else:
            raise SyntaxError(f"Expected {token_type}, found {self.current_token()}")

    def parse(self):
        """Start parsing from the top-most non-terminal <program>."""
        self.program()

    def program(self):
        """<program> ::= <stmt_list>"""
        self.stmt_list()

    def stmt_list(self):
        """<stmt_list> ::= <stmt> <stmt_list> | ε"""
        while self.current_token() and self.current_token()[0] != 'RBRACE':  # End of program or block
            self.stmt()

    def stmt(self):
        """<stmt> ::= <decl_stmt> | <assign_stmt> | <if_stmt> | <while_stmt> | <print_stmt>"""
        if self.current_token()[0] == 'INT':
            self.decl_stmt()
        elif self.current_token()[0] == 'ID':
            self.assign_stmt()
        elif self.current_token()[0] == 'IF':
            self.if_stmt()
        elif self.current_token()[0] == 'FOR':
            self.for_stmt()
        elif self.current_token()[0] == 'WHILE':
            self.while_stmt()
        elif self.current_token()[0] == 'PRINT':
            self.print_stmt()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token()}")

    def decl_stmt(self):
        """<decl_stmt> ::= 'int' ID ';'"""
        self.match('INT')
        var_name = self.current_token()[1]
        self.semantic.declare_variable(var_name)
        self.match('ID')
        self.match('SEMICOLON')


    def assign_stmt(self):
        """<assign_stmt> ::= ID '=' <expr> ';'"""
        var_name = self.current_token()[1]
        self.semantic.check_variable(var_name)
        self.match('ID')
        self.match('ASSIGN')
        expr_result = self.expr()  
        self.match('SEMICOLON')
        self.intermediate_code.append(f"{var_name} = {expr_result}")


    def if_stmt(self):
        
        self.match('IF')
        self.match('LPAREN')
        condition = self.cond()
        self.match('RPAREN')

        false_label = self.new_label()
        end_label = self.new_label()

        self.intermediate_code.append(f"ifFalse {condition} goto {false_label}")

        self.match('LBRACE')
        self.stmt_list()
        self.match('RBRACE')

        # If there is an else
        if self.current_token() and self.current_token()[0] == 'ELSE':
            self.intermediate_code.append(f"goto {end_label}")
            self.intermediate_code.append(f"{false_label}:")
            self.match('ELSE')
            self.match('LBRACE')
            self.stmt_list()
            self.match('RBRACE')
            self.intermediate_code.append(f"{end_label}:")
        else:
            self.intermediate_code.append(f"{false_label}:")



    def while_stmt(self):
        start_label = self.new_label()
        self.intermediate_code.append(f"{start_label}:")

        self.match('WHILE')
        self.match('LPAREN')
        condition = self.cond()
        self.match('RPAREN')

        false_label = self.new_label()
        self.intermediate_code.append(f"ifFalse {condition} goto {false_label}")

        self.match('LBRACE')
        self.stmt_list()
        self.match('RBRACE')

        self.intermediate_code.append(f"goto {start_label}")
        self.intermediate_code.append(f"{false_label}:")

    def for_stmt(self):
        self.match('FOR')
        self.match('LPAREN')

        # Initialization
        self.assign_stmt()

        start_label = self.new_label()
        self.intermediate_code.append(f"{start_label}:")

        # Condition
        condition = self.cond()
        self.match('SEMICOLON')
        false_label = self.new_label()
        self.intermediate_code.append(f"ifFalse {condition} goto {false_label}")

        # Increment: extract tokens until RPAREN (excluding RPAREN)
        increment_start = self.pos
        while self.tokens[self.pos][0] != 'RPAREN':
            self.pos += 1
        increment_tokens = self.tokens[increment_start:self.pos]  # Exclude RPAREN

        self.match('RPAREN')
        self.match('LBRACE')

        # Loop body
        self.stmt_list()
        self.match('RBRACE')

        # Process increment using a separate parser instance
        increment_parser = Parser(increment_tokens)
        increment_parser.pos = 0  # Ensure we start at the beginning of the increment tokens
        increment_parser.semantic = self.semantic  # Share symbol table
        increment_parser.temp_count = self.temp_count
        increment_parser.label_count = self.label_count

        increment_parser.stmt()  # Only one statement expected (e.g., i = i + 1)

        # Sync state and append generated TAC
        self.temp_count = increment_parser.temp_count
        self.label_count = increment_parser.label_count
        self.intermediate_code.extend(increment_parser.intermediate_code)

        self.intermediate_code.append(f"goto {start_label}")
        self.intermediate_code.append(f"{false_label}:")




    def print_stmt(self):
        """<print_stmt> ::= 'print' '(' ID ')'"""
        self.match('PRINT')
        self.match('LPAREN')
        var_name = self.current_token()[1]
        self.semantic.check_variable(var_name)
        self.match('ID')
        self.match('RPAREN')
        self.intermediate_code.append(f"print {var_name}")

    def cond(self):
        """<cond> ::= <expr> <relop> <expr>"""
        left = self.expr()
        op = self.relop()
        right = self.expr()
        cond_result = f"{left} {op} {right}"
        return cond_result

    def relop(self):
        if self.current_token()[0] in ['GT', 'LT', 'EQ', 'GE', 'LE']:
            op = self.current_token()[1]
            self.consume()
            return op
        else:
            raise SyntaxError(f"Unexpected token in condition: {self.current_token()}")


    def expr(self):
        """<expr> ::= <term> <expr_tail>"""
        left = self.term()
        return self.expr_tail(left)

    def expr_tail(self, left):
        """<expr_tail> ::= '+' <term> <expr_tail> | '-' <term> <expr_tail> | ε"""
        
        if self.current_token() and self.current_token()[0] in ['PLUS', 'MINUS']:
            op = self.current_token()[1]
            self.consume()
            right = self.term()
            result = self.new_temp()
            self.intermediate_code.append(f"{result} = {left} {op} {right}")
            return self.expr_tail(result)
        return left

        

        if self.current_token() and self.current_token()[0] in ['PLUS', 'MINUS']:
            op = self.current_token()[1]
            self.consume()
            right = self.term()
            temp = self.new_temp()
            self.intermediate_code.append(f"{temp} = {left} {op} {right}")
            return self.expr_tail(temp)
        return left



    def term(self):
        """<term> ::= <factor> <term_tail>"""
        left = self.factor()
        return self.term_tail(left)

    def term_tail(self,left):
        """<term_tail> ::= '*' <factor> <term_tail> | '/' <factor> <term_tail> | ε"""
        if self.current_token() and self.current_token()[0] in ['MULT', 'DIV']:
            op = self.current_token()[1]
            self.consume()
            right = self.factor()
            temp = self.new_temp()
            self.intermediate_code.append(f"{temp} = {left} {op} {right}")
            return self.term_tail(temp)
        return left

    def factor(self):
        """<factor> ::= ID | NUM | '(' <expr> ')'"""
        token = self.current_token()
        if token[0] == 'ID':
            self.semantic.check_variable(token[1])
            self.match('ID')
            return token[1]
        elif token[0] == 'NUM':
            value = token[1]
            self.match('NUM')
            return value
        elif token[0] == 'LPAREN':
            self.match('LPAREN')
            val = self.expr()
            self.match('RPAREN')
            return val
        else:
            raise SyntaxError("Unexpected token in factor")
        
    def new_temp(self):
        if not hasattr(self, 'temp_count'):
            self.temp_count = 0
        self.temp_count += 1
        return f"t{self.temp_count}"


# Example usage
from lexer import tokenize 
from lexer import code # Import the lexer from the lexer module
tokens = tokenize(code)  # Lexical analysis
parser = Parser(tokens)  # Parsing the token stream
parser.parse()  # Start parsing

print("\nGenerated Intermediate Code:")
for line in parser.intermediate_code:
    print(line)
