import pandas as pd
import openpyxl
import io

class ExcelReader:
    def __init__(self, file_content) :
        self.file_content = file_content
        
    def read_excel_with_merged_cells(self) :
        pass