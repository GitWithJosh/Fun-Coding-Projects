"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object.
"""

"""
Import statements and global variables
"""
import pygame as p
import ChessEngine, ChessAI
WIDTH = HEIGHT = 520 
DIMENSION = 8 # Dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For animations later on
IMAGES = {}
MOVE_LOG_PANEL_WIDTH = WIDTH//4
MOVE_LOG_PANEL_HEIGHT = HEIGHT

"""
Initialize a global dictionary of images.
This will be called exactly once in the main.
"""
def loadImages():
    pieces = ["wp","wR","wN","wB","wK","wQ","bp","bR","bN","bB","bK","bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess_AI/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying 'IMAGES['wp']'
"""
Draw a starting screen to ask the user if they want to play against the AI or another human.
"""
def drawStartingScreen(screen):
    global colors
    colors = [p.Color("white"), p.Color("dark green")]
    starting_image = p.image.load("Chess_AI/images/startingScreen.jpeg")
    starting_image = p.transform.scale(starting_image, (WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    screen.blit(starting_image, (0, 0))
    font = p.font.SysFont("Arial", 34, True, False)
    text = "Press 1 for Human vs Human"
    textObject = font.render(text, 0, p.Color('light gray'))
    textLocation = p.Rect(0, 0, WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT).move((WIDTH + MOVE_LOG_PANEL_WIDTH) / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2 - 75)
    screen.blit(textObject, textLocation)
    text = "Press 2 for Human vs AI"
    textObject = font.render(text, 0, p.Color('light gray'))
    textLocation = p.Rect(0, 0, WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT).move((WIDTH + MOVE_LOG_PANEL_WIDTH) / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2 - 25)
    screen.blit(textObject, textLocation)
    font = p.font.SysFont("Arial", 20, True, False)
    text = "Press g for green board, b for blue board, r for red board"
    textObject = font.render(text, 0, p.Color('light gray'))
    textLocation = p.Rect(0, 0, WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT).move((WIDTH + MOVE_LOG_PANEL_WIDTH) / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2 + 25)
    screen.blit(textObject, textLocation)
    p.display.flip()
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                quit()
            if e.type == p.KEYDOWN:
                if e.key == p.K_1:
                    return True
                if e.key == p.K_2:
                    return False
                if e.key == p.K_g:
                    colors = [p.Color("white"), p.Color("dark green")]
                if e.key == p.K_b:
                    colors = [p.Color("white"), p.Color("blue")]
                if e.key == p.K_r:
                    colors = [p.Color("white"), p.Color("red")]
"""
The main driver for our code. This will handle user input and updating the graphics.
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = () # No square is selected initially, this will keep track of the last click of the user (tuple: (row, col)).
    playerClicks = [] # Keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False
    restart = False
    playerOne = True # If a human is playing white, then this will be True. If an AI is playing, then False.
    playerTwo = drawStartingScreen(screen) # Same as above but for black.
    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            # Quit the game
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTurn:
                    location = p.mouse.get_pos() # (x,y) location of the mouse
                    col = location[0] // SQ_SIZE 
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8: # The user clicked the same square twice or clicked outside the board
                        sqSelected = ()
                        playerClicks = []
                    else: # The user clicked a new square
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: # After the second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                        
            # Key handler
            elif e.type == p.KEYDOWN:
                # Undo when 'z' is pressed and the game is not over
                if e.key == p.K_z and not gameOver:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                # Reset the board when 'r' is pressed and the game is over
                if e.key == p.K_r and gameOver:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = drawStartingScreen(screen)
                    restart = True
                # Change the players when '1' or '2' is pressed
                if e.key == p.K_1:
                    playerOne = not playerOne
                if e.key == p.K_2:
                    playerTwo = not playerTwo
        # AI move finder logic
        if not gameOver and not isHumanTurn and not restart:
            AIMove = ChessAI.findBestMoveAlphaBeta(gs, validMoves)
            if AIMove is None:
                AIMove = ChessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        if gs.checkMate or gs.staleMate:
            gameOver = True
            text = 'Stalemate' if gs.staleMate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            restart = 'Press "r" to restart'
            drawEndGameText(screen, text, 250)
            drawEndGameText(screen, restart, 300)
        if gs.remis == 50:
            gameOver = True
            text = 'Remis'
            restart = 'Press "r" to restart'
            drawEndGameText(screen, text, 250)
            drawEndGameText(screen, restart, 300)
        restart = False
        clock.tick(MAX_FPS)
        p.display.flip()

"""
Responsible for all the graphics within a current game state.
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)

"""
Draw the white and black squares on the board. The top left square is always light.
"""
def drawBoard(screen):
    global colors
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
"""
Hihglight square selected and moves for piece selected
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))   
            s.set_alpha(150)
            s.fill(p.Color("gray"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # Highlight moves from that square
            s.fill(p.Color("green"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))
"""
Draw the pieces on the board using the current GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # Not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
"""
Draw the move log
"""
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = ["MoveLog:"]
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + " "
        moveTexts.append(moveString)
        if len(moveTexts) > 30:
            moveTexts = moveTexts[:1] + moveTexts[-29:]
    movesPerRow = 1
    padding = 5
    lineSpacing = 1
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j <= len(moveLog):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing
"""
Animating a move
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 8 # Frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120)
"""
Draw text on the screen
"""
def drawEndGameText(screen, text, location_height=HEIGHT/2):
    font = p.font.SysFont("Helvetica", 40, True, False) # Type, size, bold, italics
    textObject = font.render(text, 0, p.Color('Dark Gray')) # Text, anti-aliasing, color
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, location_height - textObject.get_height()/2) # Center the text
    screen.blit(textObject, textLocation) # Draw the text
    textObject = font.render(text, 0, p.Color('Dark Red')) # Text, anti-aliasing, color
    screen.blit(textObject, textLocation.move(2,2)) # Draw the text
"""
Main driver
"""
if __name__ == "__main__":
    main()