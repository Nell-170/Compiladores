import sys
import ply.yacc as yacc
from Lexer import tokens, lexer

# Global list whit processed logs
entries = []

# Start function 
def p_log(p): 
    ''' Log : principalFunction '''
    p[0] = p[1]
    entries.append(p[0])

# Principal function
def p_principalFunction(p):
    ''' principalFunction : string entry '''

    # Create a dictionary to represent the value of 'principal Function'
    p[0] = {
        "type": "principalFunction",
        "string": p[1],  # The first element is the 'string'
        "entry": p[2]    # The second element is the 'entry'
    }
    
    # Store the result in the global entries list
    entries.append(p[0])
    

# entry
def p_entry(p):
    ''' entry : TIMESTAMP LOGLEVEL ENTRY description message entry
              | TIMESTAMP LOGLEVEL ENTRY description entry
              | empty'''
    
    # default initialization of the entry dictionary
    entry = {}

    # Handling the recursive rule (p[6] is the recursive call)
    if len(p) == 7:
        if p[1] == 'TIMESTAMP':
            entry = {
                'timestamp': p[1],
                'loglevel': p[2],
                'entry_type': p[3],
                'description': p[4],
                'message': p[5],
                'next_entry': p[6]  # The next recursive entry is added here
            }
    
    elif len(p) == 6:
        entry = {
            'timestamp': p[1],
            'loglevel': p[2],
            'entry_type': p[3],
            'description': p[4],
        }
     
    # If it is not a valid input, it is left as None
    else:
        entry = None

    # If it's empty, don't add it to the list.
    if entry is not None:
        p[0] = entry
        entries.append(p[0])



def p_string(p):
    ''' string : STRING string
               | STRING '''

def p_empty(p):
    'empty :'
    pass

# ERROR FUNCTION DEFINITION

def p_error(p):
    if p:
        print(f"Error en linea {p.lineno}: Token '{p.value}' no esperado")
    else:
        print("Error: Fin de archivo inesperado")

# D 
def p_description(p):
    '''description : object verb FINAL_POINT 
                   | object FINAL_POINT '''
    if len(p) == 4:
        # Case: description : object verb FINAL_POINT
        p[0] = {
            "object": p[1],
            "verb": p[2],
            "final_point": p[3]
        }
    elif len(p) == 3:
        # Case: description : object FINAL_POINT
        p[0] = {
            "object": p[1],
            "final_point": p[2]
        }
    entries.append(p[0])

def p_object(p): 
    ''' object : OBJECT ADJECTIVE 
               | ADJECTIVE OBJECT
               | OBJECT'''
    if len(p) == 3:
        # Case: object : OBJECT ADJECTIVE
        p[0] = {
            "object": p[1],
            "adjective": p[2]
        }
    elif len(p) == 3:
        # Case: object : ADJECTIVE OBJECT
        p[0] = {
            "adjective": p[1],
            "object": p[2]
        }
    elif len(p) == 2:
        # Case: object : OBJECT
        p[0] = {
            "object": p[1]
        }
    entries.append(p[0])

def p_verb(p): 
    ''' verb : VERB ADJECTIVE
             | ADJECTIVE
             | VERB  '''
    
    if len(p) == 3:
        # Case: verb : VERB ADJECTIVE
        p[0] = {
            "verb": p[1],
            "adjective": p[2]
        }
    elif len(p) == 2:
        if p[1] == "ADJECTIVE":
            # Case: verb : ADJECTIVE
            p[0] = {
                "adjective": p[1]
            }
        else:
            # Case: verb : VERB
            p[0] = {
                "verb": p[1]
            }

    entries.append(p[0])

def p_message(p): 
    ''' message : content 
                | content END_MESSAGE
                | END_MESSAGE '''
    
    if len(p) > 2:
        p[0] = {
            "type": "content_type",
            "content": p[1], 
            "end_message": p[2]
        }
    else:
        if p[0] == 'content':
            p[0] = {
                "type": "content_type",
                "content": p[1], 
            }
        else:
            p[0] = {
                "type": "end_message",
                "end_message": p[1],
            }
    entries.append(p[0])

def p_content(p):
    ''' content : BEGIN_CRASH_REPORT crashMessage END_CRASH_REPORT 
                | BEGIN_BACKUP beginBackupInformation END_BACKUP
                | BEGIN_BOOT_SEQUENCE bbuStep END_BOOT_SEQUENCE
                | BEGIN_DIAGNOSTIC beginDiagnosticMessage END_DIAGNOSTIC '''

    if p[1] == 'BEGIN_CRASH_REPORT':
        p[0] = {
            "type": "crash_report",
            "star": p[1], # start block 
            "data": p[2], # Whatever crash Message has returned
            "end":  p[3]  # end block
        }
    elif p[1] == 'BEGIN_BACKUP':
        p[0] = {
            "type": "backup",
            "star": p[1], 
            "data": p[2], 
            "end":  p[3]  
        }
    elif p[1] == 'BEGIN_BOOT_SEQUENCE':
        p[0] = {
            "type": "boot_sequence",
            "star": p[1], 
            "data": p[2], 
            "end":  p[3]  
        }
    elif p[1] == 'BEGIN_DIAGNOSTIC':
        p[0] = {
            "type": "diagnostic",
            "star": p[1], 
            "data": p[2], 
            "end":  p[3]  
        }
    entries.append(p[0])

# Crash message block
def p_crashMessage(p):
    ''' crashMessage :  ERROR_CODE  CRASH_MESSAGE STACK_TRACE stacktrace'''
    
    entry = {
        'error_code': p[1],
        'crash_message': p[2],
        'stack_trace': p[3]
    }

   # Store the processed message in the global entries list
    entries.append(entry)
    p[0] = entry

def p_stack_trace(p):
    ''' stacktrace : CRASH_FUN_DET  stacktrace
                   | CRASH_FUN_DET  CLOSING_SQUARE_BRACKET '''

    p[0] = p[1] + p[2]
    entries.append(p[0])

# backup block
def p_begin_backup_information(p):
    ''' beginBackupInformation : beginBackupHeader beginBackupUpdateBlock'''

    p[0] = {
        "type": "backup_information",
        "header": p[1],
        "update_block": p[2]
    }
    entries.append(p[0])

def p_begin_backup_header(p): 
    ''' beginBackupHeader : SOURCE DESTINATION_BACKUP FILE_LIST beginBackupDat '''

    p[0] = {
        "source": p[1],
        "destination_backup": p[2],
        "file_list": p[3],
        "dat_files": p[4]  # List of file numbers
    }
    entries.append(p[0])

def p_begin_backup_dat(p):
    ''' beginBackupDat : FILE_DAT beginBackupDat
                       | FILE_DAT CLOSING_SQUARE_BRACKET '''

    if len(p) == 3:  
        p[0] = p[1] + p[2]  
    else: 
        p[0] = [p[1]] 
    entries.append(p[0])

def p_begin_backup_update_block(p):
    ''' beginBackupUpdateBlock : BEGIN_BACKUP_UPDATE  beginBackupUpdateBlockData END_BACKUP_UPDATE beginBackupUpdateBlock
                               | BEGIN_BACKUP_UPDATE  beginBackupUpdateBlockData END_BACKUP_UPDATE '''

    p[0] = {
        "type": "backup_update_block",
        "data": p[2],  # update block data
        "next_block": p[4] if len(p) > 4 else None  # if necessary it is added
    }
    entries.append(p[0])

def p_begin_backup_update_block_data(p):
    ''' beginBackupUpdateBlockData : BBU_TIMESTAMP BBU_PROGRESS BBU_DETAILS'''

    p[0] = {
        "timestamp": p[1],
        "progress": p[2],
        "details": p[3]
    } 
    entries.append(p[0])

# boot_sequence block
def p_bbu_step(p):
    ''' bbuStep : BOOT_STEP bbuSteps bbuStep
                | BOOT_STEP bbuSteps '''
    
    p[0] = {
        "step_type": p[1],
        "steps": p[2],
        "next_step": p[3] if len(p) > 3 else None
    }
    entries.append(p[0])

def p_bbu_steps(p):
    ''' bbuSteps : INIT_HARDWARE 
                 | FINALIZE_BOOT 
                 | LOAD_SERVICE 
                 | START_SERVICE '''
    
    p[0] = p[1]
    entries.append(p[0])

# Diagnostic block
def p_begin_Diagnostic_Message(p):
    ''' beginDiagnosticMessage : checkFunction '''

    p[0] = {
        "type": "diagnostic_message",
        "function": p[1]
    }
    entries.append(p[0])

def p_check_Function(p):
    ''' checkFunction : CHECKS_DIAGNOSTIC CHECK_RESOURCE ARROW STATUS LATENCY NUMBER_UNIT checkFunction
                      | CHECKS_DIAGNOSTIC CHECK_RESOURCE ARROW STATUS LATENCY NUMBER_UNIT '''

    p[0] = {
        "check": p[1],
        "resource": p[2],
        "arrow": p[3],
        "status": p[4],
        "latency": p[5],
        "number_unit": p[6],
        "next_function": p[7] if len(p) > 7 else None 
    }
    entries.append(p[0])

# To test the parser
parser = yacc.yacc()

# Function to read the file and test the parser
def parser_tester(path):
    lexer.lineno = 1 # line count reset, to avoid errors due to accumulation of values
    stdout_original = sys.stdout
    
    # Reading the file
    with open(path, 'r', encoding='utf-8') as f:
        input_text = f.read()

    # Redirecting stdout to a report file
    with open("Parser_report.txt", "w") as archivoParser:
        sys.stdout = archivoParser
        try:
            result = parser.parse(input_text, lexer=lexer, debug=False)
            print("Parser completado exitosamente")
            success = True
        except Exception as e:
            print(f"Error durante el parseo: {e}")
            success = False

    # Restoring stdout
    sys.stdout = stdout_original
    return success

# Structures testing method
def structures_parser_tester():
    # Filter only errors
    errores = [ 
        e for e in entries 
        if isinstance(e, dict) and e.get('loglevel') == 'ERROR:'
    ]
    print(f"Se encontraron {len(errores)} logleves de tipo error en el archivo.")

    # export everything to JSON:
    import json

    # Convert dictionaries to JSON
    logs_json = json.dumps(entries, indent=4) 
    with open("logs.json", "w") as f:
        f.write(logs_json)


# File to analyze
path = "large_complex_log.txt"
parser_tester(path)
structures_parser_tester()