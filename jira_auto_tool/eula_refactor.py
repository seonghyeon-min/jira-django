def build_basic_data_structure(self):
    b_merged_ranges = self.get_merged_ranges_by_column(2)
    
    for b_range in b_merged_ranges:
        entry_data = {}
        
        b_value = self.get_cell_value(b_range.min_row, 2)
        entry_data['Country'] = {
            'value': b_value,
            'terms_lst': []
        }
        
        c_merged_ranges = self.get_all_ranges_by_column(3, b_range)
        
        for c_range in c_merged_ranges:
            c_value = self.get_cell_value(c_range.min_row, 3)
            
            entry_data['Country']['terms_lst'].append({
                c_value: {
                    'tp_code': []
                }
            })
            
            # Check if C column is merged
            if c_range.min_row == c_range.max_row:  # unmerged case
                current_row = c_range.min_row
                while True:
                    if self.get_cell_value(current_row, 8) != "삭제":  # Check if not deleted
                        order = self.get_cell_value(current_row, 5)  # Get order from column E
                        tp_code = self.get_cell_value(current_row, 6)
                        
                        entry_data['Country']['terms_lst'][-1][c_value]['tp_code'].append(tp_code)
                        
                        # Check if next row exists and its order is 1 (cycle complete)
                        next_order = self.get_cell_value(current_row + 1, 5)
                        if next_order == 1 or next_order is None:
                            break
                            
                    current_row += 1
            else:  # merged case
                for row in range(c_range.min_row, c_range.max_row + 1):
                    if self.get_cell_value(row, 8) != "삭제":
                        tp_code = self.get_cell_value(row, 6)
                        entry_data['Country']['terms_lst'][-1][c_value]['tp_code'].append(tp_code)
        
        self.sheet_data.append({'data': entry_data})
