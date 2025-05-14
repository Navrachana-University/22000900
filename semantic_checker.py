#semantic cheks for variables existence 

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # {variable_name: type}

    def declare_variable(self, var_name):
        if var_name in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{var_name}' already declared.")
        self.symbol_table[var_name] = 'int'

    def check_variable(self, var_name):
        if var_name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{var_name}' not declared.")
