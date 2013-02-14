from pyrem_torq import *
from pyrem_torq.expression import *
from pyrem_torq.treeseq import seq_split_nodes_of_label

# TODO We should consider to splitting process to parse two characters operators
#      such as ^= ++ --
def split_to_str(text):
    p = re.compile("|".join([
        r"/[^/\r\n]*/", r'"[^"\r\n]*"', r"\d+", # literals (regex, string, integer)
        r"#[^\r\n]*", # comment
        r"[ \t]+", r"\r\n|\r|\n", # white spaces, newline
        r"[a-zA-Z_](\w|_)*", # identifier
        r"[<>!=]=|&&|[|][|]", r"[-+*/%<>!=()${},;]|\[|\]", # operators
        r"." # invalid chars
    ]))
    return [ 'code' ] + utility.split_to_strings(text, pattern=p)

def tokenizing_expr():
    # identify reserved words, literals, identifiers
    return Search(script.compile(r"""
    (r_BEGIN <- "BEGIN") | (r_END <- "END")
    | (r_assert <- "assert")
    | (r_boolean <- "boolean") | (r_byte <- "byte") | (r_char <- "char") | (r_int <- "int" )
    | (r_double <- "double")
    | (r_float <- "float")
    | (r_false <- "false")
    | (r_next <- "next") | (r_if <- "if") | (r_else <- "else") | (r_for <- "for") | (r_while <- "while") | (r_do <- "do")
    | (r_break <- "break") | (r_continue <- "continue" ) | (r_case <- "case") | (r_catch <- "catch") | (r_default <- "default")
    | (r_finally <- "finally")
    | (r_instanceof <- "instanceof")
    | (r_long <- "long")
    | (r_new <- "new")
    | (r_null <- "null")
    | (r_return <- "return")
    | (r_short <- "short")
    | (r_switch <- "switch")
    | (r_synchronized <- "synchronized")
    | (r_this <- "this")
    | (r_throw <- "throw")
    | (r_true <- "true")
    | (r_try <- "try")
    | (r_volatile <- "volatile")
    | (id <- r"^[a-zA-Z_]") 
    | (l_integer <- r"^[0-9]") | (l_string <- r"^\"") | (l_string <- r"^'")
    | (op_xor <- "^")
    | (op_xor_eq <- "^=")
    | (op_gt <- ">") | (op_ge <- ">=") | (op_lt <- "<") | (op_le <- "<=") | (op_ne <- "!=") | (op_eq <- "==")
    | (op_and <- "&&") | (op_or <- "||")
    | (op_plusplus <- "++") | (op_minusminus <- "--")
    | (op_plus <- "+") | (op_minus <- "-") | (op_mul <- "*") | (op_div <- "/") | (op_mod <- "%")
    | (op_assign <- "=") | (op_not <- "!") | (op_dollar <- "$") | (op_or2 <- "|")
    | (LP <- "(") | (RP <- ")") | (LB <- "{") | (RB <- "}") | (LK <- "[") | (RK <- "]")
    | (dot <- ".") | (comma <- ",") | (semicolon <- ";") | (colon <- ":")
    | (ques <- "?") | (bslash <- "\\")
    | (newline <- "\r\n" | "\r" | "\n")
    | (null <- r"^[ \t#]")
    | any, error("unexpected character")
    ;"""))

# remained reserved keywords but these keyword never appear in the method maybe.
#< ABSTRACT: "abstract" >
#| < CLASS: "class" >
#| < CONST: "const" >
#| < ENUM: "enum" >
#| < EXTENDS: "extends" >
#| < FINAL: "final" >
#| < GOTO: "goto" >
#| < IMPLEMENTS: "implements" >
#| < IMPORT: "import" >
#| < INTERFACE: "interface" >
#| < NATIVE: "native" >
#| < PACKAGE: "package">
#| < PRIVATE: "private" >
#| < PROTECTED: "protected" >
#| < PUBLIC: "public" >
#| < STATIC: "static" >
#| < STRICTFP: "strictfp" >
#| < SUPER: "super" >
#| < THROWS: "throws" >
#| < TRANSIENT: "transient" >
#| < VOID: "void" >
#| < WHILE: "while" >

def create_two_singles(seq):
    singles = set()
    prev = seq.pop(0)
    for tok in seq:
        singles.add((prev[0], prev[2], tok[0], tok[2]))
        prev = tok
    #print "\n\n"
    #print singles

    return singles

def tokenize(tokenizer, script):
    seq = split_to_str(script)
    seq = tokenizer.parse(seq)
    return seq_split_nodes_of_label(seq, "null")[0]

def calculate_similarity(script1, script2):
    tokenizer = tokenizing_expr()
    seq = tokenize(tokenizer, script1)
    seq2 = tokenize(tokenizer, script2)

    singles1 = create_two_singles(seq)
    singles2 = create_two_singles(seq2)


    return len( singles1 & singles2) / float(len(singles1 | singles2))

def main():
    import sys
    
    if len(sys.argv) == 1:
        print "usage: singles -f <script> [ <input> ]\nAn calculator of method similarity for Java."
        return
    
    assert len(sys.argv) in (3, 4)
    assert sys.argv[1] == "-f"
    scriptFile = sys.argv[2]
    scriptFile2 = sys.argv[3] if len(sys.argv) == 4 else None

    f = open(scriptFile, "r")
    try:
        script = f.read()
    finally: f.close()
    script = script + "\n" # prepare for missing new-line char at the last line

    if scriptFile2 is None:
        tokenizer = tokenizing_expr()
        seq = tokenizer.parse(script)
        print "\n".join(treeseq.seq_pretty(treeseq.seq_remove_strattrs(seq)))
        return

    f = open(scriptFile2, "r")
    try:
        script2 = f.read()
    finally: f.close()
    script2 = script2 + "\n"

    calculate_similarity(script, script2)

if __name__ == '__main__':
    main()
