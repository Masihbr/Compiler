EPSILON = None
SYNCHRONOUS = 'synch'

PARSE_TABLE = {
    'Program': {
        'break': ('Statements', '#jump_main'),  # Program -> Statements #jump_main
        'continue': ('Statements', '#jump_main'),
        'ID': ('Statements', '#jump_main'),
        'return': ('Statements', '#jump_main'),
        'global': ('Statements', '#jump_main'),
        'def': ('Statements', '#jump_main'),
        'if': ('Statements', '#jump_main'),
        'while': ('Statements', '#jump_main'),
        '$': ('Statements', '#jump_main'),
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
        'break': ('break', '#break'),  # Simple_stmt -> break #break
        'continue': ('continue', '#continue'),  # Simple_stmt -> continue #continue
        'ID': ('Assignment_Call',),
        'return': ('Return_stmt',),
        'global': ('Global_stmt',),
    },
    'Compound_stmt': {
        ';': SYNCHRONOUS,
        'def': ('Function_def',),  # Compound_stmt -> Function_def
        'if': ('If_stmt',),
        'while': ('Iteration_stmt',),
    },
    'Assignment_Call': {
        ';': SYNCHRONOUS,
        'ID': ('#psym', 'ID', 'B'),  # Assignment_Call -> #psym ID #var_def_finish B
    },
    'B': {
        ';': SYNCHRONOUS,
        '=': ('#add_sym', '=', 'C', '#check_void', '#assign'),  # B -> #add_sym = C #check_void #assign
        '[': ('#check_sym', '[', 'Expression', '#index', ']', '=', 'C', '#check_void', '#assign'),  # B -> #check_sym [ Expression #index ] = C #check_void #assign
        '(': ('#check_sym', '#func_call_start', '(', 'Arguments', ')', '#func_call_finish', '#pop'),
        # B -> #check_sym #func_call_start ( Arguments ) #func_call_finish #pop
    },
    'C': {
        ';': SYNCHRONOUS,
        'ID': ('Expression',),
        '[': ('#arr_init', '[', 'Expression', '#parr', 'List_Rest', ']', '#arr_len'),
        # C -> #arr_init [ Expression #parr List_Rest ] #arr_len
        'NUM': ('Expression',),
    },
    'List_Rest': {
        ']': EPSILON,
        ',': (',', 'Expression', '#parr', 'List_Rest'),  # List_Rest -> , Expression #parr List_Rest
    },
    'Return_stmt': {
        ';': SYNCHRONOUS,
        'return': ('return', 'Return_Value', '#func_def_finish'),  # Return_stmt -> return Return_Value #func_def_finish
    },
    'Return_Value': {
        ';': (EPSILON, '#push_zero'),  # Return_Value -> '' #push_zero
        'ID': ('Expression', '#has_return_value'), # Return_Value -> Expression #has_return_value
        'NUM': ('Expression', '#has_return_value'), # Return_Value -> Expression #has_return_value
    },
    'Global_stmt': {
        ';': SYNCHRONOUS,
        'global': ('global', '#global', 'ID'), # Global_stmt -> global #global ID
    },
    'Function_def': {
        ';': SYNCHRONOUS,
        'def': ('def', '#pfunc', 'ID', '#save_func', '#set_func_start', '(', 'Params', ')', '#func_def_start', ':',
                'Statements', '#push_zero', '#func_def_finish', '#pop_func_address', '#check_func'),
        # Function_def -> def #pfunc ID #save_func #set_func_start ( Params ) #func_def_start : Statements #push_zero #func_def_finish #pop_func_address #check_func
    },
    'Params': {
        'ID': ('#pparam', 'ID', 'Params_Prime'),  # Params -> #pparam ID Params_Prime
        ')': EPSILON,
    },
    'Params_Prime': {
        ')': EPSILON,
        ',': (',', '#pparam', 'ID', 'Params_Prime'),  # Params -> #pparam ID Params_Prime
    },
    'If_stmt': {
        ';': SYNCHRONOUS,
        'if': ('if', 'Relational_Expression', '#save', ':', 'Statements', 'Else_block'),
        # If_stmt -> if Relational_Expression #save : Statements Else_block
    },
    'Else_block': {
        ';': (EPSILON, '#jpf'),  # Else_block -> '' #jpf
        'else': ('else', ':', '#jpf_save', 'Statements', '#jp'),  # Else_block -> else : #jpf_save Statements #jp
    },
    'Iteration_stmt': {
        ';': SYNCHRONOUS,
        'while': ('while', '#label', '(', 'Relational_Expression', ')', '#save', 'Statements', '#while'),
        # Iteration_stmt -> while #label ( Relational_Expression ) #save Statements #while
    },
    'Relational_Expression': {
        'ID': ('Expression', '#check_void', '#comp_op', 'Relop', 'Expression', '#check_void', '#comp'),
        # Relational_Expression -> Expression #check_void #comp_op Relop #check_void Expression #comp
        ')': SYNCHRONOUS,
        ':': SYNCHRONOUS,
        'NUM': ('Expression', '#comp_op', 'Relop', 'Expression', '#comp'),
        # Relational_Expression -> Expression #comp_op Relop Expression #comp
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
        '+': ('+', '#check_void', 'Term', '#check_void', '#add', 'Expression_Prime'),  # Expression_Prime -> + #check_void Term #check_void #add Expression_Prime
        '-': ('-', '#check_void', 'Term', '#check_void', '#sub', 'Expression_Prime'),  # Expression_Prime -> - #check_void Term #check_void #sub Expression_Prime
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
        '*': ('*', '#check_void', 'Factor', '#check_void', '#mult', 'Term_Prime'),  # Term_Prime -> * #check_void Factor #check_void #mult Term_Prime
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
        '==': ('Primary',),
        '<': ('Primary',),
        '+': ('Primary',),
        '-': ('Primary',),
        '*': ('Primary',),
        '**': ('**', '#check_void', 'Factor', '#check_void', '#power'),  # Power -> ** #check_void Factor #power
    },
    'Primary': {
        ';': EPSILON,
        '[': ('[', 'Expression', '#index', ']', 'Primary'),  # Primary -> [ Expression #index ] Primary
        ']': EPSILON,
        '(': ('#func_call_start', '(', 'Arguments', ')', '#func_call_finish', 'Primary'),
        # Primary -> #func_call_start ( Arguments ) #func_call_finish Primary
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
        'ID': ('Expression', '#add_arg', 'Arguments_Prime'),  # Arguments -> Expression #add_arg Arguments_Prime
        ')': EPSILON,
        'NUM': ('Expression', '#add_arg', 'Arguments_Prime'),  # Arguments -> Expression #add_arg Arguments_Prime
    },
    'Arguments_Prime': {
        ')': EPSILON,
        ',': (',', 'Expression', '#add_arg', 'Arguments_Prime'),
        # Arguments_Prime -> , Expression #add_arg Arguments_Prime
    },
    'Atom': {
        ';': SYNCHRONOUS,
        'ID': ('#pid', 'ID'),  # Atom -> #pid ID
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
        'NUM': ('#pnum', 'NUM'),  # Atom -> #pnum NUM
    },
}
