import ply.lex as lex
import sys

tokens = (
    'TIMESTAMP', 
    'LOGLEVEL', 
    'ENTRY',
    'END_MESSAGE',
    'ADJECTIVE',
    'OBJECT',
    'VERB',
    'FINAL_POINT',

    # CRM Block 
    'ERROR_CODE',
    'CRASH_MESSAGE',
    'STACK_TRACE',
    'CRASH_FUN_DET',

    # Principal begin and end blocks
    'BEGIN_CRASH_REPORT',
    'END_CRASH_REPORT',
    'BEGIN_BOOT_SEQUENCE',
    'END_BOOT_SEQUENCE',
    'BEGIN_DIAGNOSTIC',
    'END_DIAGNOSTIC',

    'CHECKS_DIAGNOSTIC',
    'BOOT_STEP',
    'INIT_HARDWARE',
    'FINALIZE_BOOT',
    'LOAD_SERVICE',
    'START_SERVICE',
    'CHECK_RESOURCE',

    # Begin Back_up block
    'DESTINATION_BACKUP',
    'SOURCE',
    'FILE_LIST',
    'CLOSING_SQUARE_BRACKET',
    'FILE_DAT',
    'BEGIN_BACKUP_UPDATE',
    'END_BACKUP_UPDATE',
    'BEGIN_BACKUP',
    'END_BACKUP',
    'BBU_TIMESTAMP',
    'BBU_PROGRESS',
    'BBU_DETAILS',
    
    # Begin Diagnostic Block
    'ARROW',
    'STATUS',
    'LATENCY',

    'STRING',
    'NUMBER_UNIT',
)


# ----- Token regex rules -----

# Date and time: [2025-02-15 08:00:55]
def t_TIMESTAMP(t):
    r'\s?\[\d{4}-\d{2}-\d{2}\s+·?\d{2}:\d{2}:\d{2}\]\s'
    return t

# INFO, ERROR, WARN, DEBUG
def t_LOGLEVEL(t):
    r'INFO:|ERROR:|WARN:|DEBUG:'
    return t

# Message 
def t_END_MESSAGE(t): 
    r'\#\sEnd\sof\sEntry\s\d{3}'
    return t

# Word Entry (always appears)
def t_ENTRY(t):
    r'Entry\s+\d{3,4}:'
    return t

# Adjective
def t_ADJECTIVE(t):
    r'Low|successfully|partial|successful|recorded|initiated|completed|Partial|detected|Scheduled'
    return t

def t_OBJECT(t):
    # TODO(): Tambien puede ser verbo + objeto
    r'Network\sservices|Loading\sconfiguration|Configuration|boot|Service|configuration|Driver|Module\serror|disk\sspace|User|System\sboot|Diagnostic|Application|backup|backup|drivers|hardware|services'
    return t

def t_VERB(t):
    r'running|loaded|restarted|installed|encountered|login|recorded|logout|crash|Load|Initialize|Start|Finalize'
    return t

def t_FINAL_POINT(t):
    r'\.'
    return t

# CRM BLOCK
def t_ERROR_CODE(t):
    r'ERROR_CODE:\s\d{3};'
    return t

# CRMM
def t_CRASH_MESSAGE(t):
    r'MESSAGE:\s+"Crash\sin\smodule\s[A-Z]";'
    return t

# STACK TRACE
def t_STACK_TRACE(t):
    r'STACK_TRACE:\s\[\s'
    t.lexer.lineno += t.value.count('\n')
    return t

# CRST It's necessary for repetitions

def t_CRASH_FUN_DET(t):
    r'\s*{\sFUNCTION:\s"func_\d{1}",\sLINE:\s\d+\s},'
    t.lexer.lineno += t.value.count('\n')
    return t

# Principals blocks of begin and end
def t_BEGIN_CRASH_REPORT(t):
    r'\s*BEGIN_CRASH_REPORT'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_END_CRASH_REPORT(t):
    r'\s*END_CRASH_REPORT'
    t.lexer.lineno += t.value.count('\n')
    return t

####
def t_BEGIN_BOOT_SEQUENCE(t):
    r'\s*BEGIN_BOOT_SEQUENCE'
    t.lexer.lineno += t.value.count('\n')
    return t

####
def t_END_BOOT_SEQUENCE(t):
    r'\s*END_BOOT_SEQUENCE'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_BEGIN_DIAGNOSTIC(t):
    r'\s*BEGIN_DIAGNOSTIC'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_END_DIAGNOSTIC(t):
    r'\s*END_DIAGNOSTIC'
    t.lexer.lineno += t.value.count('\n')
    return t

# Token for the boot sequence steps
def t_BOOT_STEP(t):
    r'STEP:\s'
    return t

def t_INIT_HARDWARE(t):
    r'"Initialize\shardware";'
    return t

def t_FINALIZE_BOOT(t):
    r'"Finalize\sboot";'
    return t

def t_LOAD_SERVICE(t):
    r'"Load\sdrivers";'
    return t

def t_START_SERVICE(t):
    r'"Start\sservices";'
    return t

# Begin Diagnostic Block
def t_CHECKS_DIAGNOSTIC(t):
    r'CHECK:\s'
    return t

def t_CHECK_RESOURCE(t):
    r'"network"|"storage"|"audio"|"video"'
    t.value = t.value.strip('"')  # Optional: clear the quotes
    return t

def t_STATUS(t):
    r'"pass",\s|"fail",\s'
    return t

def t_LATENCY(t):
    r'latency:\s'
    return t

# Begin Backup content
def t_SOURCE(t):
    r'SOURCE:\s"/data/source_\d+\.bin";'
    return t 

def t_DESTINATION_BACKUP(t):
    r'DESTINATION:\s"/backup/backup_\d+\.bin";'
    return t 

def t_FILE_LIST(t):
    r'FILE_LIST:\s\['
    return t

def t_CLOSING_SQUARE_BRACKET(t):
    r'\];'
    return t

def t_FILE_DAT(t):
    r'\s*"file_\d_\d+\.dat",'
    t.lexer.lineno += t.value.count('\n')
    return t 

def t_BEGIN_BACKUP_UPDATE(t):
    r'\s*BEGIN_BACKUP_UPDATE'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_BBU_TIMESTAMP(t):
    r'\s*TIMESTAMP:\s"\d{1,2}:\d{2}:\d{2}";'
    t.lexer.lineno += t.value.count('\n')
    return t

# BBU : Begin_BackUp_Update
def t_BBU_PROGRESS(t):
    r'\s*PROGRESS:\s\d{2,3};'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_BBU_DETAILS(t):
    r'\s*DETAILS:\s"Update\s\d";'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_END_BACKUP_UPDATE(t):
    r'\s*END_BACKUP_UPDATE'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_BEGIN_BACKUP(t):
    r'\s*BEGIN_BACKUP'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_END_BACKUP(t):
    r'\s*END_BACKUP'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_ARROW(t):
   #r'\s->\s{\sresult:\s'
    r'->\s*{\s*result:\s*'
    return t

# Numbers with units: 75%, 17ms, etc.
def t_NUMBER_UNIT(t):
    r'"\d+ms"\s};'
    return t

# String values ​​between quotes or single words (the lexer still needs to be further tuned)
def t_STRING(t):
    r'.+'
    return t

# Ignore spaces and tabs
t_ignore = ' \t'

# Ignore comments
def t_COMMENT(t):
    r'\#.*'
    pass

# Line breaks
def t_newline(t):
    r'(\r\n|\n|\r)+'
    t.lexer.lineno += t.value.count('\n')

# Errors
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}")
    t.lexer.skip(1)

lexer = lex.lex()

# Function to read the file and test the lexer
def lexer_tester(path):
    # The original system stdout reference is saved
    stdout_original = sys.stdout
    
    # Open the file to be tested
    with open(path, 'r', encoding='utf-8') as f:
        # The report file is created or opened for writing to
        with open("Lexer_report.txt", "w") as archivoLexer:
            sys.stdout = archivoLexer
            for line in f:
                lexer.input(line)
                for tok in lexer:
                    print(tok)
    
    # Returns system stdout to its original location
    sys.stdout = stdout_original

# File path and test
path = "large_complex_log.txt"
lexer_tester(path)