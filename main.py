import pygame

from piece import Piece
from game_board import GameBoard

class TetrisMain:
    """Main class of Tetris game. Contains all pygame display and event 
    handling while connecting both of the classes Piece and GameBoard
    together.
    """
    
    def __init__(self):
               
        self.master_display_size = (300, 500)
        self.display_offset = (10, 10)
        self.block_size = 20
        self.game_board = GameBoard(self.block_size, self.display_offset)
        
        pygame.init()
        pygame.display.set_caption("Tetris")
        game_icon = pygame.image.load("static/game_icon.png")
        pygame.display.set_icon(game_icon)
        
        self.gameDisplay = pygame.display.set_mode(self.master_display_size)
        self.clock = pygame.time.Clock()
        
        pygame.font.init()
        self.body_font = pygame.font.SysFont('Comic Sans MS', 24)
        self.header_font = pygame.font.SysFont('Comic Sans MS', 34)
        
        self.isRunning = True
        self.isPaused = False
        self.startNewGame = False
        
        # Generate random shape 
        self.live_shape_idx = 0
        self.live_piece = Piece(self.block_size, self.display_offset, self.game_board.get_next_piece())
        self.dead_pieces = []

        # Controls the movement of the live piece on the x axis
        self.x_tick = 0
        self.x_change = 0
        # How many times the piece is moved down on x axis per frame - controls piece speed on the y axis
        self.fall_count = 2
        self.drop = False

        self.score = 0
        self.main()
        
    def main(self):
        """Main game loop.
        """
        
        while self.isRunning:
            
            # Check for user events
            self.event_handler()
            
            if not self.game_board.hasLost and not self.isPaused:
                
                # Move piece down; left/right/drop/pause depending on events
                self.move_piece()
                    
                # Check if shape is dead/bottom has collided with object
                if self.live_piece.bottom_collision:
                    self.convert_live2dead()
                    # !!! Revisit random shape selection
                    self.live_piece = Piece(self.block_size, 
                                            self.display_offset,
                                            self.game_board.get_next_piece())
                    
                # Check for full rows
                self.handle_full_rows()
                
                # Draw screen
                self.draw_screen()
                
            elif self.isPaused:
                self.draw_screen()
                
            elif self.game_board.hasLost:
                if not self.startNewGame:
                    self.draw_screen()
                    self.draw_game_over_screen()
                else:                  
                    self.start_new_game()
            
            self.x_tick += 1
            pygame.display.update()
            self.clock.tick(30)
                        
    def event_handler(self):
        """Handles all user inputs: clicks and keystrokes.
        """
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isRunning = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.x_change = -self.block_size
                elif event.key == pygame.K_RIGHT:
                    self.x_change = self.block_size
                elif event.key == pygame.K_UP:
                    self.live_piece.rotate(self.game_board.board)
                elif event.key == pygame.K_DOWN:
                    self.fall_count = 10
                elif event.key == pygame.K_SPACE:
                    self.fall_count = self.block_size*24
                    self.drop = True
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.x_change = 0
                elif event.key == pygame.K_DOWN or event.key == pygame.K_SPACE:
                    self.fall_count = 2

            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                # Mouse click over pause button
                if 222 <= pygame.mouse.get_pos()[0] <= 285 and 425 <= pygame.mouse.get_pos()[1] <= 475:
                    self.isPaused = not self.isPaused
                
                # If game has been lost
                if self.game_board.hasLost:
                    # User clicked the play again button
                    if 45 <= pygame.mouse.get_pos()[0] <= 125 and 115 <= pygame.mouse.get_pos()[1] <= 175:
                        self.startNewGame = True
                    
                    # User clicked the quit button
                    elif 170 <= pygame.mouse.get_pos()[0] <= 250 and 115 <= pygame.mouse.get_pos()[1] <= 175:
                        self.isRunning = False
                                        
    def move_piece(self):
        """Handles moving the self.live_piece down, left, and right.
        """
        
        if self.x_change != 0 and self.x_tick % 2 == 0:
            self.live_piece.move_side(self.x_change, self.game_board.board)

        for i in range(self.fall_count):
            self.live_piece.move_down(self.game_board.board)
            # Reset self.fall_count value after using spacebar to drop piece
            if self.live_piece.isLive and self.drop:
                self.fall_count = 2
                self.drop = False
                    
    def convert_live2dead(self):
        """Handles toggling boolean self.live_piece.isLive to False and stores
        coordinates of all blocks in piece in self.game_board.board to later 
        reference for possible collisions.
        """
        
        self.live_piece.isLive = False
                    
        self.live_piece.update_top_collision()
        if self.live_piece.top_collision:
            self.game_board.hasLost = True
            
        for y_idx, row in enumerate(self.live_piece.coordinates):
            for x_idx, coords in enumerate(row):
                # Filter out all placeholder blocks in self.live_piece.shape
                if self.live_piece.shape[y_idx][x_idx] != '0':
                    self.game_board.activate_position(coords) 
                    
        self.dead_pieces.append(self.live_piece)
        
    def handle_full_rows(self):
        """Check if any row in self.game_board.board is full and delete blocks.
        Clear pieces no longer visible on the board from self.dead_pieces and
        refresh self.game_board.board. Rewards points for clearing rows, bonus
        for clearing more than 1 row with 1 piece.
        """
        
        full_rows = self.game_board.get_full_rows()
        if full_rows != None:
            # Award points - the more cleared by 1 piece, the more points
            if len(full_rows) == 1:
                self.score += 40
            else:
                self.score += int(40*len(full_rows)*1.5)
                
            for row in full_rows:
                self.game_board.handle_full_row(row)
                for piece in self.dead_pieces:
                    piece.delete_row_idx(row)
                    piece.drop_dead_down(row)
            
            # Filter out pieces that are no longer visible on the board
            self.dead_pieces = [piece for piece in self.dead_pieces if piece.isVisible]
            
            # Refresh board
            self.game_board.refresh_board(self.dead_pieces)
            
    def start_new_game(self):
        """Resets all existing cells from previous game to the initial new game blank defaults.
        """
        
        self.game_board = GameBoard(self.block_size, self.display_offset)
        
        self.isRunning = True
        self.isPaused = False
        self.startNewGame = False
        
        # Generate the next random shape
        self.live_shape_idx = 0
        self.live_piece = Piece(self.block_size, self.display_offset, 
                                self.game_board.get_next_piece())
        self.dead_pieces = []
        
        self.score = 0
        
        self.main()
        
    def draw_screen(self):
        """Handles bliting everything on to the screen.
        """    

        self.gameDisplay.fill((255, 255, 255))
        self.blit_border()
        
        for piece in self.dead_pieces:
            self.blit_piece(piece)
        self.blit_piece(self.live_piece)
                
    def blit_piece(self, piece):
        """Draws a piece on the game screen.
        """
        
        border_img = pygame.image.load("static/block_border.png")
        for y_idx, row in enumerate(piece.coordinates):
            for x_idx, coords in enumerate(row):
    
                if piece.shape[y_idx][x_idx] != '0' and coords != ['x', 'y']:
                    loc_data = (coords[0], coords[1], piece.block_size, piece.block_size)
                    pygame.draw.rect(self.gameDisplay, piece.color, loc_data)
                    self.gameDisplay.blit(border_img, (coords[0], coords[1]))
    
    def blit_border(self):
        """Draws border around the Tetris game and Pause/Play button.
        """
        
        interface_img = pygame.image.load("static/screen_hallow.png")
        self.gameDisplay.blit(interface_img, (0, 0))
        
        # Blit the play/pause icon
        if self.isPaused:
            pause_img = pygame.image.load("static/play_icon.png")
        else:
            pause_img = pygame.image.load("static/pause_icon.png")
            
        self.gameDisplay.blit(pause_img, (230, 420))            
                
        # Blit the live game score
        score_text = self.body_font.render('{}'.format(self.score), False, (0, 0, 0))
        
        # Centers score -> -8 pixels for each digit in number
        x = 246 - 8*(len(str(self.score))-1)
        self.gameDisplay.blit(score_text, (x, 18))
            
    def draw_game_over_screen(self):
        """Draws Game Over Screen with buttons to play again or exit game.
        """
        
        game_over_img = pygame.image.load("static/game_over_screen.png")
        # game_over_screen dimensions 250x150px
        x_pos = self.master_display_size[0]/2 - 125
        y_pos = 60
        self.gameDisplay.blit(game_over_img, (x_pos, y_pos))
        
        # Add Game Over Header Text
        game_over_text = self.header_font.render("Game Over", False, (0, 0, 0))
        self.gameDisplay.blit(game_over_text, (x_pos+35, y_pos+10))
        
        # Add Play Again Button
        play_again_text1 = self.body_font.render("Play", False, (0, 0, 0))
        play_again_text2 = self.body_font.render("Again", False, (0, 0, 0))
        self.gameDisplay.blit(play_again_text1, (x_pos+40, y_pos+70))
        self.gameDisplay.blit(play_again_text2, (x_pos+30, y_pos+95))
        
        # Add Quit Button
        quit_text = self.body_font.render("Quit", False, (0, 0, 0))
        self.gameDisplay.blit(quit_text, (x_pos+160, y_pos+85))
        
        
if __name__ == "__main__":
    game = TetrisMain()
    pygame.quit()
    quit()
