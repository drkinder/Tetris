class Piece:
    """Handles all creation, movement, and coordinate storage of all game
    pieces.
    """
    
    def __init__(self, block_size, display_offset, shape_code):
        """Requires block_size, int defining the len/width of each block,
        display_offset, tuple (x, y) defining how much offset the game should
        have from top left corner, and shape_code to define which shape the
        piece should be.
        """
               
        self.block_size = block_size
        self.display_width = self.block_size*10
        self.display_height = self.block_size*24
        
        self.x_offset = display_offset[0]
        self.y_offset = display_offset[1]
    
        self.isLive = True
        self.isVisible = True
        
        self.left_collision = False
        self.right_collision = False
        self.bottom_collision = False
        self.top_collision = False
        self.rotation_collision = False

        self.shape = []
        self.color = ()
        self.initialize_shape(shape_code)

        self.coordinates = []
        self.initialize_coords()
        self.set_pivot_idx()
        
    def initialize_shape(self, shape_code):
        """Initializes self.shape and self.color for the provided shape_code.
        1 represents a game block sprite, 0 no sprite. p represents a pivot sprite, the block that the piece will rotate
        around.
        """
        
        # Square
        if shape_code == 1:
            self.shape = ["11",
                          "11"]
            self.color = (216, 219, 226)
        # Line    
        elif shape_code == 2:
            self.shape = ["1p11"]
            self.color = (39, 169, 225)

        # L    
        elif shape_code == 3:
            self.shape = ["001",
                          "1p1"]
            self.color = (29, 132, 181)

        # J
        elif shape_code == 4:
            self.shape = ["100",
                          "1p1"]
            self.color = (83, 134, 228)

        # T
        elif shape_code == 5:
            self.shape = ["010",
                          "1p1"]
            self.color = (23, 96, 135)
            
        # Z
        elif shape_code == 6:
            self.shape = ["110",
                          "0p1"]
            self.color = (169, 188, 208)
            
        # S
        elif shape_code == 7:
            self.shape = ["011",
                          "1p0"]
            self.color = (83, 162, 190)

    def initialize_coords(self):
        """Initializes self.coordinates to contain the coordinates of the 
        initial starting position for each block in shape at the top center of 
        the screen.
        """

        center_x = int(self.display_width/2)-self.block_size*2
        for y_idx, row in enumerate(self.shape):
            self.coordinates.append([])
            for x_idx, block in enumerate(row):
                x = center_x + x_idx*self.block_size
                y = y_idx*self.block_size
                self.coordinates[y_idx].append([x, y])
        
        self.apply_offset()
    
    def apply_offset(self):
        """Updates self.coordinates to account for declared (x, y) offset.
        """
        
        if self.x_offset or self.y_offset:
            for y_idx, row in enumerate(self.coordinates):
                for x_idx, coord in enumerate(row):
                    self.coordinates[y_idx][x_idx] = [coord[0] + self.x_offset, coord[1] + self.y_offset]
       
    def set_pivot_idx(self):
        """Finds index of pivot 'p' inside self.shape to use as a relative 
        origin for piece rotation.
        """
        
        for y_idx, row in enumerate(self.shape):
            for x_idx, block in enumerate(row):
                if block == 'p':
                    self.pivot = (y_idx, x_idx)
                    return
        self.pivot = None
        
    def move_side(self, amount, board):
        """Checks game_board.board to ensure that movement will not cross
        outside of the play area or cause overlap with any existing pieces.
        Will move the piece += parameter amount on the x-axis.
        """
        
        self.update_left_collision(board)
        self.update_right_collision(board)
        
        if amount > 0 and not self.right_collision:
            for y_idx, row in enumerate(self.coordinates):
                for x_idx, coord in enumerate(row):
                    self.coordinates[y_idx][x_idx][0] += amount
                    
        elif amount < 0 and not self.left_collision:
            for y_idx, row in enumerate(self.coordinates):
                for x_idx, coord in enumerate(row):
                    self.coordinates[y_idx][x_idx][0] += amount
              
    def move_down(self, board):
        """Checks game_board.board to ensure that movement will not cross
        outside of the play area or cause overlap with any existing pieces.
        Will move the piece +1 on the y-axis. Call i times per frame to move
        +i on the y axis
        """
        
        self.update_bottom_collision(board)
        
        if not self.bottom_collision:
            for y_idx, row in enumerate(self.coordinates):      
                for x_idx, block in enumerate(row):
                    check = self.coordinates[y_idx][x_idx][1] + 1
                    self.coordinates[y_idx][x_idx][1] = check
    
    def drop_dead_down(self, y_index):
        """Drops down all blocks < y_index*self.block_size 1 self.block_size.
        """

        max_y = y_index*self.block_size
        for y_idx, row in enumerate(self.coordinates):
            for x_idx, coord in enumerate(row):
                if coord != ['x', 'y']:
                    if coord[1] < max_y:
                        self.coordinates[y_idx][x_idx][1] += self.block_size
                  
    def rotate(self, board):
        """After ensuring that rotation will not cause collision, calls 
        self.rotate_shape and self.rotate_coordinates to rotate both
        self.shape and self.coordinates 90 degrees clock-wise.
        """
        
        self.update_rotation_collision(board)
        
        # Box shape doesn't rotate
        if not self.rotation_collision and self.pivot is not None:        
            self.shape = self.rotate_matrix_90d(self.shape)
            self.coordinates = self.rotate_coordinates()
            self.set_pivot_idx()
                
    def rotate_coordinates(self):
        """Returns a list of self.coordinates rotated 90 degrees clock-wise
        with updated new coordinates.
        """
        
        pivot_coords = self.coordinates[self.pivot[0]][self.pivot[1]]
        
        rotated_coords = []
        
        for idx_y, row in enumerate(self.coordinates):
            rotated_coords.append([])
            for block in row:
                # Get distance of block from pivot
                relative_coords = self.get_relative_pos(block, pivot_coords)
                # Rotate coordinates 90 degrees via relative axis (pivot block)
                new_relative_coords = [relative_coords[1], -relative_coords[0]]
                # Return coordinates to (x, y) in relation to real pivot loc
                new_coords = [new_relative_coords[0]+pivot_coords[0], new_relative_coords[1]+pivot_coords[1]]
                rotated_coords[idx_y].append(new_coords)
            
        return self.rotate_matrix_90d(rotated_coords)

    @staticmethod
    def rotate_matrix_90d(matrix):
        """Returns matrix rotated 90 degrees clock-wise. 
        """
        
        rotated90 = zip(*matrix[::-1])
        
        rotated = []
        for row in rotated90:
            rotated.append(list(row))
            
        return rotated

    @staticmethod
    def get_relative_pos(coords, relative_axis_coords):
        
        relative_pos = (relative_axis_coords[0]-coords[0], relative_axis_coords[1]-coords[1])
        return relative_pos
    
    def update_isVisible(self):
        """Toggles self.isVisible True/False depending on whether coordinates
        corresponding to visible blocks exist.
        """
        
        for y_idx, row in enumerate(self.coordinates):
            for x_idx, coord in enumerate(self.coordinates):
                if coord != ['x', 'y'] and self.shape[y_idx][x_idx] != '0':
                    self.isVisible = True
                    return
        self.isVisible = False
            
    def delete_row_idx(self, row_idx):
        """Replaces all coordinates in self.coordinates with ['x', 'y'] if 
        y == row_idx*self.block_size.
        """
        
        target_y = row_idx*self.block_size + self.y_offset
        for y_idx, row in enumerate(self.coordinates):
            if row[0][1] == target_y: #if y == target_y
                for x_idx, coord in enumerate(row):
                    self.coordinates[y_idx][x_idx] = ['x', 'y']
        
    def update_left_collision(self, board):
        """Toggles self.left_collision True/False based on whether next move
        will cross-over existing block or the width of the display.
        """
        
        hitlist = self.get_left_hitlist(board)
        
        # Check to make sure the block isn't touching the max of display_width
        for coord in hitlist:
            if coord[0] < self.x_offset:
                self.left_collision = True
                return
        
        # Check to make sure the user's next move won't cross over an existing game_piece
        for y_idx, row in enumerate(board):
            for x_idx, block in enumerate(row):
                if block == 1:
                    x = x_idx*self.block_size + self.x_offset
                    y = y_idx*self.block_size + self.y_offset
                    if [x, y] in hitlist:
                        self.left_collision = True
                        return
                    
        self.left_collision = False
    
    def get_left_hitlist(self, board):
        """Returns a list with coordinates of all blocks directly touching 
        each left-most block (smallest x) in each row of a piece.
        """
        
        hitlist = []
        for y_idx, row in enumerate(self.shape):
            x = 0
            while self.shape[y_idx][x] == '0':
                x += 1
            subtract_y = (self.coordinates[y_idx][x][1]-self.y_offset) % 20
            y = self.coordinates[y_idx][x][1]-subtract_y
            hitlist.append([self.coordinates[y_idx][x][0]-self.block_size, y])
                    
        return hitlist
    
    def update_right_collision(self, board):
        """Toggles self.right_collision True/False based on whether next move
        will cross-over existing block or the width of the display.
        """
        
        hitlist = self.get_right_hitlist(board)
        
        # Check to make sure block isn't touching the max of display_width
        for coord in hitlist:
            if coord[0] >= self.display_width:
                self.right_collision = True
                return
        
        # Check to make sure next move won't overloop existing game_piece
        for y_idx, row in enumerate(board):
            for x_idx, block in enumerate(row):
                if block == 1:
                    x = x_idx*self.block_size + self.x_offset
                    y = y_idx*self.block_size + self.y_offset
                    if [x, y] in hitlist:
                        self.right_collision = True
                        return
                    
        self.right_collision = False
    
    def get_right_hitlist(self, board):
        """Returns a list with coordinates of all blocks directly touching the
        each right-most block(largest x) in each row of a piece.
        """
        
        hitlist = []
        for y_idx, row in enumerate(self.shape):
            x = -1
            while self.shape[y_idx][x] == '0':
                x -= 1            
            subtract_y = ((self.coordinates[y_idx][x][1] - self.y_offset) % self.block_size)
            y = self.coordinates[y_idx][x][1]-subtract_y
            hitlist.append([self.coordinates[y_idx][x][0]+self.block_size, y])
                    
        return hitlist
    
    def update_bottom_collision(self, board):
        """Toggles self.bottom_collision True/False based on whether next move
        will cross-over existing block or the length of the display.
        """
        
        hitlist = self.get_bottom_hitlist()
        
        # Check to make sure block isn't touching the bottom of display_height
        for coord in hitlist:
            if coord[1] == self.display_height + self.y_offset:
                self.bottom_collision = True
                return
            
        for y_idx, row in enumerate(board):
            for x_idx, block in enumerate(row):
                if block == 1:
                    x_check = x_idx*self.block_size + self.x_offset
                    y_check = y_idx*self.block_size + self.y_offset
                    if [x_check, y_check] in hitlist:
                        self.bottom_collision = True
                        return
        
        self.bottom_collision = False
        
    def get_bottom_hitlist(self):
        """Returns a list with coordinates of all blocks directly below
        of all bottom-most blocks (largest y) in a piece.
        """
        
        hitlist = []
        for idx, block in enumerate(self.shape[-1]):
            y = -1
            while self.shape[y][idx] == '0':
                y -= 1
            hitlist.append([self.coordinates[y][idx][0], self.coordinates[y][idx][1]+self.block_size])
                    
        return hitlist

    def update_top_collision(self):
        """Loops through all boxes on top of shape and toggles 
        self.top_collision True/False based on whether top of piece is touching
        the top of the display->(box_y == self.y_offset).
        """
        
        for idx, block in enumerate(self.shape[0]):
            if block != '0':
                if self.coordinates[0][idx][1] == self.y_offset:
                    self.top_collision = True
                    return
            
        self.top_collision = False
        
    def update_rotation_collision(self, board):
        """Checks coordinates of following rotation to see if rotation will
        cause collision with game boundaries or existing box. Toggles boolean
        self.rotation_collision True/False accordingly.
        """
        
        # Square piece does not rotate
        if self.pivot is not None:
            hitlist = self.get_rotation_hitlist()
            
            # Check if rotation will exceed x-axis play area
            for coords in hitlist:
                if coords[0] < self.x_offset or coords[0] > self.display_width - self.x_offset:
                    self.rotation_collision = True
                    return
            
            # Check if rotation will cause collision with existing game pieces
            for y_idx, row in enumerate(board):
                for x_idx, block in enumerate(row):
                    if block == 1:
                        x_check = x_idx*self.block_size + self.x_offset
                        y_check = y_idx*self.block_size + self.y_offset
                        if [x_check, y_check] in hitlist:
                            self.rotation_collision = True
                            return
            
            self.rotation_collision = False
  
    def get_rotation_hitlist(self):
        """Returns a list with coordinates of all blocks occupying the position
        that would be covered if self.coordinates were rotated 90 degrees
        clock-wise.
        """
        
        hitlist = []
        rotated_coordinates = self.rotate_coordinates()
        
        for row in rotated_coordinates:
            for coords in row:
                hitlist.append([coords[0], coords[1]-coords[1]%self.block_size])
                    
        return hitlist
