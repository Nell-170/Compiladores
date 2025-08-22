# Library to handle dates and time
from datetime import datetime 
import sys

# Reads a text file and returns a list of lines
def read_file(path):
    
    with open(path, 'r', encoding = 'utf-8') as f:
        return f.readlines()

'''
Counts the amount of each category.
There are 4 categories: ERROR, WARN, INFO, and DEBUG.
It also counts the total number of log entries and returns all the data at the end.
'''
def count_categories(lines):

    total = len([l for l in lines if l.strip().startswith("[")])
    errors = [l for l in lines if "ERROR:" in l]
    warnings = [l for l in lines if "WARN:" in l]
    info = [l for l in lines if "INFO:" in l]
    debug = [l for l in lines if "DEBUG:" in l]
    
    return total, errors, warnings, info, debug

'''
Prints a summary of the text file, showing the total number of
log entries, the count of each category, and the last update date.
'''
def print_summary(total, errors, warnings, info, debug):

    print("System Summary:")
    print("---------------------")
    print(f"Total Log Entries: {total}")
    print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Message Types:")
    print("---------------------")
    print(f"INFO      : {len(info)}")
    print(f"DEBUG     : {len(debug)}")
    print(f"WARNING   : {len(warnings)}")
    print(f"ERROR     : {len(errors)}")
    print()

'''
This is where the "analysis" of the file happens, where the file is opened to
count its data and print them, so the functions are called.
'''
def analyze_logs(path):

    lines = read_file(path)
    total, errors, warnings, info, debug = count_categories(lines)
    print_summary(total, errors, warnings, info, debug)
    return total, errors, warnings, info, debug


'''
 Function to get a more detailed error and warning report
'''
def deeply_analyze_logs(path):

    lines = read_file(path)
    total, errors, warnings, info, debug = count_categories(lines)
    
    # Dictionaries for detailed analysis
    error_types = {}
    error_details = {}
    
    # Detailed error analysis
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Search for error lines
        if "ERROR:" in line:
            # Extract date and time
            date_time = line[1:line.find("]")]
            
            # Extract error description (what comes after "Entry X:")
            desc_start = line.find("Entry")
            if desc_start != -1:
                # Find the end of "Entry XX:"
                end_entry = line.find(":", desc_start)

                if end_entry != -1:
                    # Extract the real description
                    description = line[end_entry + 1:].strip()
                    
                    # Count this type of error
                    if description in error_types:
                        error_types[description] += 1
                    else:
                        error_types[description] = 1
                    
                    # Check if there is a detailed error report following
                    if i + 1 < len(lines) and "BEGIN_CRASH_REPORT" in lines[i + 1]:
                        error_info = {"date": date_time, "lines": []}
                        j = i + 1
                        
                        # Collect all lines from the error report
                        while j < len(lines) and "END_CRASH_REPORT" not in lines[j]:
                            error_info["lines"].append(lines[j].strip())
                            
                            # Extract error code if present
                            if "ERROR_CODE:" in lines[j]:
                                error_code = lines[j].split("ERROR_CODE:")[1].strip().rstrip(";")
                                error_info["code"] = error_code
                            
                            # Extract message if present
                            if "MESSAGE:" in lines[j]:
                                message = lines[j].split("MESSAGE:")[1].strip().rstrip(";")
                                error_info["message"] = message
                            
                            j += 1
                            
                        # Add this detailed error to our collection
                        if description in error_details:
                            error_details[description].append(error_info)
                        else:
                            error_details[description] = [error_info]
                        
                        # Move the main index forward to skip the processed report
                        i = j + 1
                        continue
        
        i += 1
    
    # print_summary(total, errors, warnings, info, debug)
    print_detailed_errors(error_types, error_details)
    return total, errors, warnings, info, debug, error_types, error_details

# Prints a detailed analysis of the errors
def print_detailed_errors(error_types, error_details):

    print("Detailed Error Analysis:") 
    print("-----------------------------")
    print()

    if error_types:
        # Sort errors by frequency (from highest to lowest)
        sorted_errors = sorted(error_types.items(), key = lambda x: x[1], reverse = True)
        
        for description, count in sorted_errors:
            print(f"- {description}: {count} occurrences")
            
            # If we have additional details for this type of error
            if description in error_details:
                error_codes = {}
                
                # Count error codes for this type
                for detail in error_details[description]:
                    if "code" in detail:
                        code = detail["code"]
                        if code in error_codes:
                            error_codes[code] += 1
                        else:
                            error_codes[code] = 1
                
                # Show error codes if any
                if error_codes:
                    print("  Error codes found:")
                    for code, count in error_codes.items():
                        print(f"  - Code {code}: {count} occurrences")
                    
                # Show the example message for the first error of this type
                first_detail = error_details[description][0]
                if "message" in first_detail:
                    print(f"  Example message: {first_detail['message']}")
                print(f"  First occurrence: {first_detail['date']}")
            
            print()
    else:
        print("No errors were found to analyze.")

def read_description(path):
    lines = read_file(path)
    reading_section = False
    section_content = []

    header_count = 0

    for line in lines:
        # Check if this is a header line
        if line.strip() == "# ==================================================":
            header_count += 1
            
            if header_count == 2:
                break
            elif header_count == 1:
                reading_section = True
            continue
        if reading_section:
            # Remove the leading '#' and any extra whitespace if inside the section
            if line.strip().startswith("#"):
                line = line.lstrip('#').lstrip()

            section_content.append(line.strip())

    # Combine the section content into a single string
    return "\n".join(section_content)

# Gets the logs from a range of time
def read_time(path, start_time, end_time, category_type):
    lines = read_file(path)
    logs = []
    last_date = False
    if category_type == "ALL":
        while last_date == False:
            for line in lines:
                if line.strip().startswith("["):
                    date = line[1:line.find("]")]
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    if date >= start_time and date <= end_time:
                        logs.append(line.strip())
                    elif date > end_time:
                        last_date = True
                        break
    else:
        while last_date == False:
            for line in lines:
                if category_type in line:
                    if line.strip().startswith("["):
                        date = line[1:line.find("]")]
                        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        if date >= start_time and date <= end_time:
                            logs.append(line.strip())
                        elif date > end_time:
                            last_date = True
                            break
    return logs

# Function to print the entire report to a file
def errorsAndWarningsReportGenerator(path):
    # Save the original reference to sys.stdout
    stdout_original = sys.stdout
    
    # Redirect to file (overwrite)
    with open("System status report.txt", "w") as archivo:
        sys.stdout = archivo
        
        # Calling methods that generate output
        analyze_logs(path)
        deeply_analyze_logs(path)
        
        # Restore stdout
        sys.stdout = stdout_original
    
    print("Process completed. output saved in 'System status report.txt'")