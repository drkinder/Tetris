import random


class GameBoard:
    """
    Class for handling the entire Tetris game board.
    """

    def __init__(self, block_size, display_offset):
        """
        :param block_size: the pixel height and width of a single block sprite. Allows you to dynamically resize each
        Tetris piece.
        :param display_offset: The (X, Y) offset of the game board from the top left corner of the Pygame window. This
        allows us to have a static visual frame around the play area.
        """

        self.block_size = block_size

        # The integers used below determine the ratio of the game board.
        # By default, the board should be 10 blocks wide and 24 blocks high.
        self.display_width = self.block_size*10
        self.display_height = self.block_size*24

        self.x_offset = display_offset[0]
        self.y_offset = display_offset[1]
        
        self.hasLost = False

        self.center_x = int((self.display_width/self.block_size)/2)
        self.center_y = int((self.display_height/self.block_size)/2)
        
        self.next_piece_idx = 0
        self.rand_pieces = random.sample([i for i in range(1, 8)], 7)

        self.generate_board()
        
    def generate_board(self):
        """Builds the empty 2D game board. Empty cells are represented by 0 and populated cells by 1. The size of the
        board is sized dynamically based on the values of self.block_size, self.display_width, and self.display_height.
        """
        self.board = []
        for y in range(int(self.display_height/self.block_size)):
            self.board.append([])
            for x in range(int(self.display_width/self.block_size)):
                self.board[y].append(0)
                
    def refresh_board(self, dead_shapes):
        """Generates a fresh board that properly reflects the existing
        coordinates of all dead shapes.
        """
        self.generate_board()
        
        for shape in dead_shapes:
            for y_idx, row in enumerate(shape.coordinates):
                for x_idx, coords in enumerate(row):
                    if coords != ['x', 'y'] and shape.shape[y_idx][x_idx] != '0':
                        self.activate_position(coords)
      
    def offset_coords(self, coords):
        """Allows the game board to be offset within the Pygame window so that you can have a user interface frame
        around the board."""
        return [coords[0] + self.x_offset, coords[1] + self.y_offset]

    def activate_position(self, coords):
        """Mark a cell on the board at the provided coords as active.
        """
        x_idx = int(coords[0]/self.block_size)
        y_idx = int(coords[1]/self.block_size)
        
        self.board[y_idx][x_idx] = 1
        
    def deactivate_position(self, coords):
        """Mark a cell on the board at the provided coords as inactive.
        """
        x_idx = int(coords[0]/self.block_size)
        y_idx = int(coords[1]/self.block_size)
        
        self.board[y_idx][x_idx] = 0
        
    def get_full_rows(self):
        """Returns a list with the y indices of all full rows on the board, returns None if no rows are full.
        """
        full_rows = []
        
        for y_idx, row in enumerate(self.board):
            if all(block == 1 for block in row):
                full_rows.append(y_idx)
        
        if len(full_rows) > 0:
            return full_rows
        else:
            return None
    
    def handle_full_row(self, row_index):
        """Clear all full rows from the board and drop all pieces above the cleared row down.
        """
        self.clear_row(row_index)
        self.drop_rows_down(row_index)
        
    def clear_row(self, row_index):
        """Clears all cells in the provided row_index in self.board by setting them to 0.
        """
        for idx, x in enumerate(self.board[row_index]):
            self.board[row_index][idx] = 0
    
    def drop_rows_down(self, row_threshhold_index):
        """Drops all the active cells in the rows above the row_threshold_index down 1 position on the board.
        """
        self.board.pop(row_threshhold_index)
        
        new_row = [0 for i in self.board[0]]
        self.board.insert(0, new_row)
    
    def get_next_piece(self):
        """Returns the shapecode for the next piece, after displaying all 7 
        shapes (every 7th time called) self.rand_pieces order will be shuffled.
        """
        
        next_shapecode = self.rand_pieces[self.next_piece_idx]
        self.next_piece_idx += 1
        
        if self.next_piece_idx == 7:
            self.rand_pieces = random.sample([i for i in range(1, 8)], 7)
            self.next_piece_idx = 0
        
        return next_shapecode
