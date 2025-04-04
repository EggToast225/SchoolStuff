def string_with_arrows(text, pos_start, pos_end):
    """
    Generates a string that highlights a specific portion of `text` using '^' symbols.
    
    Parameters:
    - text (str): The full text where the error occurred.
    - pos_start (Position): The starting position of the error.
    - pos_end (Position): The ending position of the error.
    
    Returns:
    - str: The formatted string with arrows pointing to the error.
    """
        
    result = ''

    # Find the start of the line containing pos_start
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)

    # Find the end of the line containing pos_end
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: # If there's no newline, take the entire text
        idx_end = len(text)
    
    # Count how many lines the error spans
    line_count = pos_end.ln - pos_start.ln + 1

    for i in range(line_count):
        # Get the current line
        line = text[idx_start:idx_end] #Get the line of the error

        # Start at the error position for the first line
        if i == 0:
            col_start = pos_start.col - 1 
        else:
            col_start = 0
        
        # End at the error position for the last line
        if i == line_count - 1:
            col_end = pos_end.col - 1
        else:
            col_end = len(line) - 1


        # Append the actual line
        result += line + '\n'

        # Append the ^ markers
        result += ' ' * col_start + '^' * (col_end - col_start + 1) + '\n'

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    # Remove tab characters to maintain alignment
    return result.replace('\t', '')