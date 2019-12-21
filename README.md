# Tetris
My Python Tetris clone using Pygame.

![alt text](readme_imgs/gameplay.gif)
## Setup
The project works immediately out of the box by executing the main.py file.

## Usage
In the Static folder, you'll find all of the custom graphics for the project.

game_board.py contains the class GameBoard for keeping track of the status (filled/empty) of each cell in the game.
  -Although the static frame png around the game board cannot be resized, the game board itself can. By tweaking the display_width
   and display_height variables in the GameBoard class, you can completely customize the dimensions of the game.
   
piece.py contains the class Piece for constructing and rotating different pieces.
  -Within the initialize_shape method of the class Piece, you can easily create your own unique blocks to use in the game.
  
main.py's class TetrisMain handles the Pygame window, drawing on the window, and handling the user's input.

## Customize

game_board.py 
  -Although the static frame png around the game board cannot be resized, the game board itself can. By tweaking the display_width
   and display_height variables in the GameBoard class, you can completely customize the dimensions of the game.
  -If you would like to change the dimensions of the static frame around the Tetris board, you can correctly place the board within
   the desired play area by setting the x_offset and y_offset variables in the GameBoard class. The x_offset should be how far from
   the left edge of the game window you would like the play area to begin and the y_offset should be how far down from the top of 
   the game window you would like the play area to begin. 
   
piece.py
  -Within the initialize_shape method of the class Piece, you can easily create your own unique blocks to use in the game.
  
## Contact
If you have any questions about this project, please email me at dylkinder@gmail.com.

Enjoy!
