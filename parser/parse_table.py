EPSILON = None
SYNCHRONOUS = 'synch'

PARSE_TABLE = {
    'Program': {
        'break': ('Statements',),
        'continue': ('Statements',),
        'ID': ('Statements',),
        'return': ('Statements',),
        'global': ('Statements',),
        'def': ('Statements',),
        'if': ('Statements',),
        'while': ('Statements',),
        '$': ('Statements',),
    },
    'Statements': {
        ';': EPSILON,
        'break': ('Statement', ';', 'Statements'),
        'continue': ('Statement', ';', 'Statements'),
        'ID': ('Statement', ';', 'Statements'),
        'return': ('Statement', ';', 'Statements'),
        'global': ('Statement', ';', 'Statements'),
        'def': ('Statement', ';', 'Statements'),
        'if': ('Statement', ';', 'Statements'),
        'else': EPSILON,
        'while': ('Statement', ';', 'Statements'),
        '$': EPSILON,
    },
    'Statement': {
        ';': SYNCHRONOUS,
        'break': ('Simple_stmt',),
        'continue': ('Simple_stmt',),
        'ID': ('Simple_stmt',),
        'return': ('Simple_stmt',),
        'global': ('Simple_stmt',),
        'def': ('Compound_stmt',),
        'if': ('Compound_stmt',),
        'while': ('Compound_stmt',),
    },
    'Simple_stmt': {
        ';': SYNCHRONOUS,
        'break': ('break',),
        'continue': ('continue',),
        'ID': ('Assignment_Call',),
        'return': ('Return_stmt',),
        'global': ('Global_stmt',),
    },
    'Compound_stmt': {
        ';': SYNCHRONOUS,
        'def': ('Function_def',),
        'if': ('If_stmt',),
        'while': ('Iteration_stmt',),
    },
    'Assignment_Call': {
        ';': SYNCHRONOUS,
        'ID': ('#pid', 'ID', 'B'), # Assignment_Call -> #pid ID B
    },
    'B': {
        ';': SYNCHRONOUS,
        '=': ('=', 'C', '#assign'), # = C #assign
        '[': ('[', 'Expression', ']', '=', 'C', '#assign'), # B -> [ Expression ] = C #assign
        '(': ('(', 'Arguments', ')', '#func_call_finish'), # B -> ( Arguments ) #func_call_finish
    },
    'C': {
        ';': SYNCHRONOUS,
        'ID': ('Expression',),
        '[': ('[', 'Expression', 'List_Rest', ']'),
        'NUM': ('Expression',),
    },
    'List_Rest': {
        ']': EPSILON,
        ',': (',', 'Expression', 'List_Rest'),
    },
    'Return_stmt': {
        ';': SYNCHRONOUS,
        'return': ('return', 'Return_Value'),
    },
    'Return_Value': {
        ';': EPSILON,
        'ID': ('Expression',),
        'NUM': ('Expression',),
    },
    'Global_stmt': {
        ';': SYNCHRONOUS,
        'global': ('global', 'ID'),
    },
    'Function_def': {
        ';': SYNCHRONOUS,
        'def': ('def', '#pid', 'ID', '#set_func_start', '(', 'Params', ')', ':', 'Statements'), # Function_def -> def #pid ID #set_func_start ( Params ) : Statements
    },
    'Params': {
        'ID': ('#pid', 'ID', 'Params_Prime'), # Params -> #pid ID Params_Prime
        ')': EPSILON,
    },
    'Params_Prime': {
        ')': EPSILON,
        ',': (',', '#pid', 'ID', 'Params_Prime'), # Params -> #pid ID Params_Prime
    },
    'If_stmt': {
        ';': SYNCHRONOUS,
        'if': ('if', 'Relational_Expression', '#save', ':', 'Statements', 'Else_block'), # If_stmt -> if Relational_Expression #save : Statements Else_block
    },
    'Else_block': {
        ';': (EPSILON, '#jpf'), # Else_block -> '' #jpf
        'else': ('else', ':', '#jpf_save', 'Statements', '#jp'), # Else_block -> else : #jpf_save Statements #jp
    },
    'Iteration_stmt': {
        ';': SYNCHRONOUS,
        'while': ('while', '(', 'Relational_Expression', ')', 'Statements'),
    },
    'Relational_Expression': {
        'ID': ('Expression', '#comp_op', 'Relop', 'Expression', '#comp'), # Relational_Expression -> Expression #comp_op Relop Expression #comp
        ')': SYNCHRONOUS,
        ':': SYNCHRONOUS,
        'NUM': ('Expression', '#comp_op', 'Relop', 'Expression', '#comp'), # Relational_Expression -> Expression #comp_op Relop Expression #comp
    },
    'Relop': {
        'ID': SYNCHRONOUS,
        '==': ('==',),
        '<': ('<',),
        'NUM': SYNCHRONOUS,
    },
    'Expression': {
        ';': SYNCHRONOUS,
        'ID': ('Term', 'Expression_Prime'),
        ']': SYNCHRONOUS,
        ')': SYNCHRONOUS,
        ',': SYNCHRONOUS,
        ':': SYNCHRONOUS,
        '==': SYNCHRONOUS,
        '<': SYNCHRONOUS,
        'NUM': ('Term', 'Expression_Prime'),
    },
    'Expression_Prime': {
        ';': EPSILON,
        ']': EPSILON,
        ')': EPSILON,
        ',': EPSILON,
        ':': EPSILON,
        '==': EPSILON,
        '<': EPSILON,
        '+': ('+', 'Term', 'Expression_Prime'),
        '-': ('-', 'Term', 'Expression_Prime'),
    },
    'Term': {
        ';': SYNCHRONOUS,
        'ID': ('Factor', 'Term_Prime'),
        ']': SYNCHRONOUS,
        ')': SYNCHRONOUS,
        ',': SYNCHRONOUS,
        ':': SYNCHRONOUS,
        '==': SYNCHRONOUS,
        '<': SYNCHRONOUS,
        '+': SYNCHRONOUS,
        '-': SYNCHRONOUS,
        'NUM': ('Factor', 'Term_Prime'),
    },
    'Term_Prime': {
        ';': EPSILON,
        ']': EPSILON,
        ')': EPSILON,
        ',': EPSILON,
        ':': EPSILON,
        '==': EPSILON,
        '<': EPSILON,
        '+': EPSILON,
        '-': EPSILON,
        '*': ('*', 'Factor', 'Term_Prime'),
    },
    'Factor': {
        ';': SYNCHRONOUS,
        'ID': ('Atom', 'Power'),
        ']': SYNCHRONOUS,
        ')': SYNCHRONOUS,
        ',': SYNCHRONOUS,
        ':': SYNCHRONOUS,
        '==': SYNCHRONOUS,
        '<': SYNCHRONOUS,
        '+': SYNCHRONOUS,
        '-': SYNCHRONOUS,
        '*': SYNCHRONOUS,
        'NUM': ('Atom', 'Power'),
    },
    'Power': {
        ';': ('Primary',),
        '[': ('Primary',),
        ']': ('Primary',),
        '(': ('Primary',),
        ')': ('Primary',),
        ',': ('Primary',),
        ':': ('Primary',),
        '==':('Primary',),
        '<': ('Primary',),
        '+': ('Primary',),
        '-': ('Primary',),
        '*': ('Primary',),
        '**': ('**', 'Factor'),
    },
    'Primary': {
        ';': EPSILON,
        '[': ('[', 'Expression', ']', 'Primary'),
        ']': EPSILON,
        '(': ('(', 'Arguments', ')', 'Primary'),
        ')': EPSILON,
        ',': EPSILON,
        ':': EPSILON,
        '==': EPSILON,
        '<': EPSILON,
        '+': EPSILON,
        '-': EPSILON,
        '*': EPSILON,
    },
    'Arguments': {
        'ID': ('Expression', 'Arguments_Prime'),
        ')': EPSILON,
        'NUM': ('Expression', 'Arguments_Prime'),
    },
    'Arguments_Prime': {
        ')': EPSILON,
        ',': (',', 'Expression', 'Arguments_Prime'),
    },
    'Atom': {
        ';': SYNCHRONOUS,
        'ID': ('#pid', 'ID'), # Atom -> #pid ID
        '[': SYNCHRONOUS,
        ']': SYNCHRONOUS,
        '(': SYNCHRONOUS,
        ')': SYNCHRONOUS,
        ',': SYNCHRONOUS,
        ':': SYNCHRONOUS,
        '==': SYNCHRONOUS,
        '<': SYNCHRONOUS,
        '+': SYNCHRONOUS,
        '-': SYNCHRONOUS,
        '*': SYNCHRONOUS,
        '**': SYNCHRONOUS,
        'NUM': ('#pnum','NUM'), # Atom -> #pnum NUM
    },
}
