import pygame
import random
import sys

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

CARD_WIDTH = 121
CARD_HEIGHT = 188

SUITS = ['H', 'D', 'C', 'S']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
# using dictionary to assign a color to each card based on suit this helps with step iv)
COLORS = {'H': 'red', 'D': 'red', 'C': 'black', 'S': 'black'}


class Card:
    def __init__(self, rank, suit, face_up=False):
        self.rank = rank  # (iii) Card values are appropriately displayed
        self.suit = suit  # (ii) Card suits are appropriately displayed
        self.color = COLORS[suit]
        self.face_up = face_up
        self.face_up_image = pygame.image.load(
            f"assets/front_card/{rank}{suit}.png")  # (i) Front side of the card is displayed
        self.face_down_image = pygame.image.load("assets/back_card/back.png")  # (i) Back side of the card is displayed
        self.image = self.face_down_image if not face_up else self.face_up_image
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

    def flip(self):
        self.face_up = not self.face_up
        self.image = self.face_up_image if self.face_up else self.face_down_image
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

    def faceUp(self):
        self.face_up = True
        self.image = self.face_up_image
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))


# following classes are used to ensure game logic with adding and transfering cards
class Pile:
    def __init__(self):
        self.cards = []
        self.pos_x = 0
        self.pos_y = 0

    def add_card(self, card):
        self.cards.append(
            card)  # (iii) As cards are sorted into their piles, they must be subtracted from the full deck of cards.

    def remove_card(self, card):
        self.cards.remove(card)


class Tableau(Pile):
    def __init__(self):
        super().__init__()

    def can_add(self, card):
        if not self.cards:
            return card.rank == 'K'  # (v) Spare tableau spots can only be filled with kings
        else:
            top_card = self.cards[-1]
            return COLORS[card.suit] != COLORS[top_card.suit] and RANKS.index(card.rank) == RANKS.index(
                top_card.rank) - 1  # (iv) Tableau cards can only be stacked in alternating colors

    def setTB(self):
        card_spacing = 20
        for i, card in enumerate(self.cards):
            card.card_x = self.pos_x
            card.card_y = self.pos_y + i * card_spacing


class Foundation(Pile):
    def can_add(self, card):
        if not self.cards:
            return card.rank == 'A'  # (vi) Foundations can only be filled starting with an ace
        else:
            top_card = self.cards[-1]
            return card.suit == top_card.suit and RANKS.index(card.rank) == RANKS.index(
                top_card.rank) + 1  # (i) Rank of cards is functional

    def setFnd(self):
        for i, card in enumerate(self.cards):
            card.card_x = self.pos_x
            card.card_y = self.pos_y


class Waste(Pile):
    def setWaste(self):
        if self.cards:
            for i, card in enumerate(self.cards):
                card.card_x = self.pos_x + i * 25
                card.card_y = self.pos_y


class Deck(Pile):
    def __init__(self):
        # declaring deck of cards and setting the image plus scaling
        super().__init__()
        self.cards = []
        self.deck_image = pygame.image.load("assets/back_card/back.png")  # (i) Back side of the card is displayed
        self.deck_image = pygame.transform.scale(self.deck_image, (CARD_WIDTH, CARD_HEIGHT))

    def fill(self):
        # filling deck with cards by using a for loop
        for suit in SUITS:
            for rank in RANKS:
                card = Card(rank, suit)
                self.cards.append(card)  # (ii) A full deck of cards is implemented.
                print(len(self.cards))

    def clearDeck(self):
        self.cards.clear()

    def shuffle(self):
        random.shuffle(self.cards)  # (ii) Deck can be shuffled

    def deal(self, tableau_piles):
        # ensure the right amount of cards are placed per tableau
        for i in range(7):
            for j in range(i + 1):
                card = self.cards.pop()  # (iii) cards are sorted into their piles, than subtracted from full deck
                tableau_pile = tableau_piles[i]
                tableau_pile.add_card(card)
                if j == i:
                    card.flip()

    def deckClicked(self, waste_pile):
        for i in range(3):
            card = self.cards.pop()
            waste_pile.add_card(card)
            card.flip()
        waste_pile.setWaste()

        print(len(self.cards))


class GameInterface:
    def __init__(self, game):
        self.cards = None
        self.game = game
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Solitaire")
        self.screen.fill((0, 128, 0))
        self.selected_card = None
        self.start_button_rect = pygame.Rect(10, 10, 100, 50)
        self.initial_mouse_pos = None
        self.selected_tableau = None

    def draw_start_button(self):
        # drawring start button i need to add functionality to potentially switch it to a restart button after clicked
        button_width = 75
        button_height = 50
        button_color = (200, 200, 200)
        if not self.game.cards_dealt:
            button_text = "Start"
        else:
            button_text = "Restart"

        button_rect = pygame.Rect(10, 10, button_width, button_height)
        pygame.draw.rect(self.screen, button_color, button_rect)

        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_start_button_click(self):
        print("Before click", self.game.start_button_clicked)
        if not self.game.cards_dealt:
            self.game.setup()
            self.game.cards_dealt = False
            self.game.start_button_clicked = True
        else:
            self.game.restart_game()
            self.game.setup()
            self.game.cards_dealt = False
        print("After click", self.game.start_button_clicked)

    def draw_tableau_piles(self):
        for tableau_pile in self.game.tableau_piles:
            tableau_pile.setTB()
            for card in tableau_pile.cards:
                self.screen.blit(card.image, (card.card_x, card.card_y))

    def draw_deck(self):
        deck_x = 100
        deck_y = 50
        # the deck is drawn on the top left of the screen but need to add space for cards when clicked
        self.screen.blit(self.game.deck.deck_image, (deck_x, deck_y))

    def draw_waste_pile(self):
        for card in self.game.waste_pile.cards:
            self.screen.blit(card.image, (card.card_x, card.card_y))

    def draw_foundation_piles(self):
        for foundation_pile in self.game.foundation_piles:
            if foundation_pile.cards:
                # drawing card
                self.screen.blit(foundation_pile.cards[-1].image, (foundation_pile.pos_x, foundation_pile.pos_y))
            else:
                # drawing rectangle
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 (foundation_pile.pos_x, foundation_pile.pos_y, CARD_WIDTH, CARD_HEIGHT), 1)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if self.start_button_rect.collidepoint(mouse_pos):
                    self.handle_start_button_click()
                else:
                    self.handle_mouse_button_down(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.handle_mouse_button_up(event.pos)

            if event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)

    def handle_mouse_button_down(self, mouse_pos):
        print("Mouse button down triggered")
        self.initial_mouse_pos = mouse_pos
        self.process_pile_down(self.game.tableau_piles, mouse_pos)

        # Deck collide point
        deck_rect = pygame.Rect(100, 50, CARD_WIDTH, CARD_HEIGHT)
        if deck_rect.collidepoint(mouse_pos):
            self.game.deck.deckClicked(self.game.waste_pile)
        
        self.process_pile_down([self.game.waste_pile], mouse_pos, is_waste=True)

    def process_pile_down(self, pile_group, mouse_pos, is_waste=False):
        for pile in pile_group:
            if pile.cards:
                top_card = pile.cards[-1]
                card_rect = pygame.Rect(top_card.card_x, top_card.card_y, CARD_WIDTH, CARD_HEIGHT)
                if card_rect.collidepoint(mouse_pos):
                    self.selected_card = top_card
                    if not is_waste:
                        self.selected_tableau = pile
                        self.selected_card_index = pile.cards.index(top_card)
                        print(f"Selected card: {self.selected_card.rank + self.selected_card.suit}", flush=True)
                        print(f"selected card x: {self.selected_card.card_x}")
                        print(f"selected card y: {self.selected_card.card_y}")
                        print(f"Selected card index: {self.selected_card_index}")
                    else:
                        print(self.selected_card.rank + self.selected_card.suit)
                        self.selected_card_index = self.game.waste_pile.cards.index(top_card)
                    return True
        return False

    def handle_mouse_button_up(self, mouse_pos):
        print("Mouse button up triggered")
        self.initial_mouse_pos = mouse_pos
        if self.selected_card:
            self.process_pile(self.game.tableau_piles, mouse_pos)
            self.process_pile(self.game.foundation_piles, mouse_pos, is_foundation=True)

        # clear selected card after mouse is released
        self.selected_card = None
        self.selected_card_index = None
        self.selected_tableau = None

    def process_pile(self, pile_group, mouse_pos, is_foundation=False):
        for pile in pile_group:
            pos_x, pos_y = (pile.cards[-1].card_x, pile.cards[-1].card_y) if pile.cards else (pile.pos_x, pile.pos_y)
            pile_rect = pygame.Rect(pos_x, pos_y, CARD_WIDTH, CARD_HEIGHT)

            if pile_rect.collidepoint(mouse_pos) and pile.can_add(self.selected_card):
                pile.add_card(self.selected_card)

                if self.selected_tableau:
                    self.selected_tableau.remove_card(self.selected_card)
                    if self.selected_tableau.cards:
                        self.selected_tableau.cards[-1].faceUp()
                    if is_foundation:
                        print(self.selected_tableau)
                else:
                    self.game.waste_pile.remove_card(self.selected_card)
                
                return True
        return False

    def handle_mouse_motion(self, mouse_pos):
        if self.selected_card:
            self.selected_card_x = mouse_pos[0] - CARD_WIDTH / 2
            self.selected_card_y = mouse_pos[1] - CARD_HEIGHT / 2

    # render screen and piles
    def render(self):
        self.screen.fill((0, 128, 0))
        self.draw_tableau_piles()
        self.draw_foundation_piles()
        self.draw_waste_pile()

        if self.game.start_button_clicked:
            self.draw_deck()

        self.draw_start_button()
        pygame.display.update()


class Game:
    def __init__(self):
        self.tableau_piles = [Tableau() for _ in range(7)]
        self.foundation_piles = [Foundation() for _ in range(4)]
        self.waste_pile = Waste()
        self.deck = Deck()
        self.setup()
        self.start_button_clicked = False
        self.cards_dealt = False
        self.game_in_progress = False

    # logic to restart game
    def restart_game(self):
        # Clear all piles and reset game state
        for tableau_pile in self.tableau_piles:
            tableau_pile.cards.clear()
        for foundation_pile in self.foundation_piles:
            foundation_pile.cards.clear()
        self.waste_pile.cards.clear()
        self.cards_dealt = False

    # logic to set pile positions and card offsets
    def setPiles(self):
        tb_spacing = 20
        for i, tableau_pile in enumerate(self.tableau_piles):
            tableau_pile.pos_x = 100
            tableau_pile.pos_y = 300

            tableau_pile.pos_x += i * (CARD_WIDTH + tb_spacing)

        for i, foundation_pile in enumerate(self.foundation_piles):
            foundation_pile.pos_x = WINDOW_WIDTH - 100 - 4 * CARD_WIDTH
            foundation_pile.pos_y = 20

            foundation_pile.pos_x += i * (CARD_WIDTH + 20)

        self.waste_pile.pos_x = 250
        self.waste_pile.pos_y = 50

    # game setup logic for start/restart
    def setup(self):
        self.deck.clearDeck()
        self.deck.fill()  # (ii) A full deck of cards is implemented.
        self.deck.shuffle()  # (ii) Deck can be shuffled
        self.setPiles()

    # run game logic
    def run(self):
        pygame.init()
        interface = GameInterface(self)
        while True:
            interface.events()
            if self.start_button_clicked and not self.cards_dealt:
                self.deck.deal(self.tableau_piles)
                self.cards_dealt = True
            interface.render()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
