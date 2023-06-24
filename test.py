import pygame
import random
import sys

# Constants for window size
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

CARD_WIDTH = 121
CARD_HEIGHT = 188

SUITS = ['H', 'D', 'C', 'S']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

class Card:
    def __init__(self, rank, suit, face_up=False):
        self.rank = rank
        self.suit = suit
        self.face_up = face_up
        self.face_up_image = pygame.image.load(f"assets/front_card/{rank}{suit}.png")
        self.face_down_image = pygame.image.load("assets/back_card/back.png")
        self.image = self.face_down_image if not face_up else self.face_up_image
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

    def flip(self):
        self.face_up = not self.face_up
        self.image = self.face_up_image if self.face_up else self.face_down_image
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

class Pile:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

class Tableau(Pile):
    pass

class Foundation(Pile):
    pass

class Waste(Pile):
    pass

class Deck:
    def __init__(self):
        self.cards = []

    def fill(self):
        for suit in SUITS:
            for rank in RANKS:
                card = Card(rank, suit)
                self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, tableau_piles):
        for i in range(7):
            for j in range(i+1):
                card = self.cards.pop()
                tableau_pile = tableau_piles[i]
                tableau_pile.add_card(card)

class GameInterface:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Solitaire")
        self.screen.fill((0, 128, 0))  # Fill the screen with green color


    def draw_start_button(self):
        button_width = 100
        button_height = 50
        button_color = (200, 200, 200)
        button_text = "Start"

        button_rect = pygame.Rect(10, 10, button_width, button_height)
        pygame.draw.rect(self.screen, button_color, button_rect)

        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_tableau_piles(self):
        pile_x = 100
        pile_y = 200
        pile_spacing = 20

        for tableau_pile in self.game.tableau_piles:
            for i, card in enumerate(tableau_pile.cards):
                card_x = pile_x
                card_y = pile_y + i * pile_spacing
                self.screen.blit(card.image, (card_x, card_y))

            pile_x += CARD_WIDTH + pile_spacing

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(10, 10, 100, 50)

                if button_rect.collidepoint(mouse_pos):
                    self.game.start_button_clicked = True

    def render(self):
        self.draw_start_button()
        pygame.display.update()

        if self.game.start_button_clicked:
            self.game.start_button_clicked = False
            self.game.deck.deal(self.game.tableau_piles)  # Deal cards using the Deck class
            pygame.time.delay(100)

            for tableau_pile in self.game.tableau_piles:
                for i, card in enumerate(tableau_pile.cards):
                    if not card.face_up:
                        card.flip()
                    pygame.time.delay(100)
                    self.screen.fill((0, 128, 0))
                    self.draw_tableau_piles()
                    pygame.display.update()

        pygame.display.update()

class Game:
    def __init__(self):
        self.tableau_piles = [Tableau() for _ in range(7)]
        self.foundation_piles = [Foundation() for _ in range(4)]
        self.waste_pile = Waste()

        self.deck = Deck()
        self.setup()

        self.start_button_clicked = False  # Track if the start button is clicked

    def setup(self):
        self.deck.fill()
        self.deck.shuffle()

    def run(self):
        pygame.init()
        interface = GameInterface(self)
        while True:
            interface.events()
            interface.render()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()