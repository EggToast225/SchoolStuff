class Position:
    def __init__(self, idx, ln, col, file_name, file_txt): # this is the index, line, column, file name and file text
        self.idx = idx
        self.ln = ln
        self.col = col
        self.file_name  = file_name
        self.file_txt = file_txt
    
    def advance(self, current_char = None): # keeps track of index and column
        self.idx += 1
        self.col += 1

        if current_char == '\n': # reset the column and increase line count if there's a newline
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.file_name, self.file_txt)