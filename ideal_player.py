import random
from typing import List, Tuple, Dict

class MemoryGameSimulator:
    def __init__(self, rows: int, cols: int, verbose: bool = True):
        self.rows = rows
        self.cols = cols
        self.total_cards = rows * cols
        self.total_pairs = self.total_cards // 2
        self.board = []
        self.revealed = {}  # Store what we've seen: {position: symbol}
        self.matched = set()  # Store positions of matched cards
        self.moves = 0
        self.perfect_matches = 0
        self.exploratory_moves = 0
        self.verbose = verbose
        
    def setup_board(self):
        """Create a shuffled board with pairs of symbols"""
        symbols = list(range(self.total_pairs))
        pairs = symbols + symbols
        random.shuffle(pairs)
        
        # Convert to 2D board
        self.board = []
        idx = 0
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(pairs[idx])
                idx += 1
            self.board.append(row)
    
    def get_position(self, row: int, col: int) -> Tuple[int, int]:
        """Convert row, col to position tuple"""
        return (row, col)
    
    def is_matched(self, pos: Tuple[int, int]) -> bool:
        """Check if a position has been matched"""
        return pos in self.matched
    
    def get_symbol(self, pos: Tuple[int, int]) -> int:
        """Get the symbol at a position"""
        row, col = pos
        return self.board[row][col]
    
    def find_known_match(self, symbol: int) -> Tuple[int, int] or None:
        """Check if we know where the matching card is"""
        positions = [pos for pos, sym in self.revealed.items() 
                    if sym == symbol and pos not in self.matched]
        return positions[0] if positions else None
    
    def get_unmatched_positions(self) -> List[Tuple[int, int]]:
        """Get all positions that haven't been matched yet"""
        unmatched = []
        for i in range(self.rows):
            for j in range(self.cols):
                pos = (i, j)
                if pos not in self.matched:
                    unmatched.append(pos)
        return unmatched
    
    def play_turn(self) -> bool:
        """
        Play one turn as an ideal player.
        Returns True if game continues, False if game is over.
        """
        if len(self.matched) == self.total_cards:
            return False
        
        # Get all unmatched positions
        unmatched = self.get_unmatched_positions()
        
        # Strategy: Try to find a known match first
        for pos in unmatched:
            if pos not in self.revealed:
                continue
            symbol = self.revealed[pos]
            match_pos = self.find_known_match(symbol)
            
            if match_pos and match_pos != pos:
                # We know where both cards are! Make a perfect match
                self.make_move(pos, match_pos, is_known_match=True)
                return True
        
        # No known matches, so explore two unrevealed cards
        unrevealed = [pos for pos in unmatched if pos not in self.revealed]
        
        if len(unrevealed) >= 2:
            pos1, pos2 = unrevealed[0], unrevealed[1]
            self.make_move(pos1, pos2, is_known_match=False)
            return True
        elif len(unrevealed) == 1:
            # Only one unrevealed card left, pair it with a known card
            pos1 = unrevealed[0]
            pos2 = [pos for pos in unmatched if pos in self.revealed][0]
            self.make_move(pos1, pos2, is_known_match=False)
            return True
        
        return False
    
    def make_move(self, pos1: Tuple[int, int], pos2: Tuple[int, int], is_known_match: bool):
        """Execute a move (flip two cards)"""
        symbol1 = self.get_symbol(pos1)
        symbol2 = self.get_symbol(pos2)
        
        # Reveal both cards in memory
        self.revealed[pos1] = symbol1
        self.revealed[pos2] = symbol2
        
        if symbol1 == symbol2:
            # Match found!
            self.matched.add(pos1)
            self.matched.add(pos2)
            
            if is_known_match:
                self.perfect_matches += 1
                if self.verbose:
                    print(f"  Turn {self.moves + 1}: PERFECT MATCH at {pos1} and {pos2} (symbol {symbol1})")
            else:
                if self.verbose:
                    print(f"  Turn {self.moves + 1}: Lucky match at {pos1} and {pos2} (symbol {symbol1})")
        else:
            # No match
            self.moves += 1
            self.exploratory_moves += 1
            if self.verbose:
                print(f"  Turn {self.moves}: No match at {pos1} (symbol {symbol1}) and {pos2} (symbol {symbol2})")
    
    def play_game(self):
        """Play a complete game"""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Starting new game: {self.rows}x{self.cols} board ({self.total_pairs} pairs)")
            print(f"{'='*60}\n")
        
        self.setup_board()
        
        turn_count = 0
        while self.play_turn():
            turn_count += 1
            if turn_count > 1000:  # Safety check
                if self.verbose:
                    print("Game exceeded maximum turns!")
                break
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"GAME COMPLETE!")
            print(f"{'='*60}")
            print(f"Total moves (wrong guesses): {self.moves}")
            print(f"Perfect matches (from memory): {self.perfect_matches}")
            print(f"Exploratory moves (revealing new cards): {self.exploratory_moves}")
            print(f"Total pairs matched: {len(self.matched) // 2}")
            print(f"Total turns taken: {self.moves + self.perfect_matches}")
            

        return self.moves


def run_simulations(rows: int, cols: int, num_games: int = 10, verbose: bool = False):
    """Run multiple simulations and show statistics"""
    if verbose:
        print(f"\n{'#'*60}")
        print(f"Running {num_games} simulations for {rows}x{cols} board")
        print(f"{'#'*60}")
    
    results = []
    for i in range(num_games):
        if verbose:
            print(f"\n--- Simulation {i+1}/{num_games} ---")
        sim = MemoryGameSimulator(rows, cols, verbose=verbose)
        moves = sim.play_game()
        results.append(moves)
    
    print(f"\n{'#'*60}")
    print(f"SUMMARY STATISTICS FOR {rows}x{cols} BOARD")
    print(f"{'#'*60}")
    print(f"Number of simulations: {num_games}")
    print(f"Average wrong moves: {sum(results) / len(results):.2f}")
    print(f"Minimum wrong moves: {min(results)}")
    print(f"Maximum wrong moves: {max(results)}")
    print(f"Total pairs: {(rows * cols) // 2}")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    # Define available board sizes
    board_sizes = {
        '3x4': (4, 3),  # rows, cols (vertical x horizontal)
        '4x4': (4, 4),
        '4x5': (5, 4),
        '5x6': (6, 5),
        '6x6': (6, 6)
    }
    
    # Set verbose mode
    VERBOSE = False  # Change to True for detailed turn-by-turn output
    
    # Run a single detailed game (with verbose output)
    if VERBOSE:
        print("EXAMPLE: Single detailed game")
        sim = MemoryGameSimulator(4, 4, verbose=True)
        sim.play_game()
        
        print("\n" + "="*60)
        print("RUNNING MULTIPLE SIMULATIONS FOR DIFFERENT BOARD SIZES")
        print("="*60)
    
    # Run multiple simulations for different board sizes
    for size_name, (rows, cols) in board_sizes.items():
        run_simulations(rows, cols, num_games=100000, verbose=VERBOSE)