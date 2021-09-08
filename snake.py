from random import randint, choice

import pygame
from search import Search

pygame.init()


class Snake:
    def __init__(self, r_blocks: int, c_blocks: int, ):
        assert (c_blocks >= 13 and r_blocks >= 13), \
            ValueError("Parameters 'c_blocks' and 'r_blocks' should not be less than 13")

        # Snake Game Variables
        self.c_blocks = c_blocks
        self.r_blocks = r_blocks
        self.direction = None
        self.snake = None
        self.food = None
        self.alive = True
        self.running = True
        self.moved_after_turn = True
        self.pause = False

        # Screen Display
        self.blocks = []
        self.block_size = 20
        self.gap = 1
        self.width = c_blocks * self.block_size + (c_blocks + 1) * self.gap
        self.height = r_blocks * self.block_size + (r_blocks + 1) * self.gap

        # Score Board
        self.score = 0
        with open('high_score.txt', 'r') as hs:
            self.high_score = int(hs.read())

        self.board_height = int(self.height * (10 / 100))
        self.board_rect = \
            pygame.Rect((self.gap, self.gap), (self.width - (2 * self.gap), self.board_height - (2 * self.gap)))
        self.height += self.board_height

        mid_pos = (int((self.width - (2 * self.gap)) / 2))
        text_gap = 10
        self.s_pos = (text_gap, text_gap)
        self.hs_pos = (mid_pos + text_gap, text_gap)

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.font_color = (61, 178, 255)

        self.score_text = self.font.render("Score: " + str(self.score), True, self.font_color)
        self.high_score_text = self.font.render("High Score: " + str(self.high_score), True, self.font_color)

        # Screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"Snake Game({self.r_blocks}, {self.c_blocks})")

        # Colors
        self.body_color = (0, 255, 0)
        self.head_color = (255, 0, 0)
        self.blocks_color = (52, 58, 64)
        self.food_color = (233, 59, 129)
        self.bg_color = (0, 0, 0)

        # Mapping
        positions = [(x, y) for x in range(self.r_blocks) for y in range(self.c_blocks)]
        self.number_map = {number: positions[number] for number in range(len(positions))}
        self.position_map = {position: number for number, position in self.number_map.items()}
        del positions

        # Adding blocks
        x, y = self.gap, self.gap + self.board_height
        for i in range(self.r_blocks):
            row_blocks = []
            for j in range(self.c_blocks):
                row_blocks.append([pygame.Rect((x, y), (self.block_size, self.block_size)), 'empty'])
                x += self.block_size + self.gap
            self.blocks.append(row_blocks)
            x = self.gap
            y += self.block_size + self.gap
        self.reset()
        self.main()

    def reset(self):
        """
        Resets the game randomly.
        """
        head_init = (randint(6, self.r_blocks - 7), randint(6, self.c_blocks - 7))
        rand_direction = choice(['u', 'd', 'l', 'r'])
        if rand_direction == 'u':
            body_init1, body_init2 = (head_init[0] - 1, head_init[1]), (head_init[0] - 2, head_init[1])
            self.direction = 'd'
        elif rand_direction == 'd':
            body_init1, body_init2 = (head_init[0] + 1, head_init[1]), (head_init[0] + 2, head_init[1])
            self.direction = 'u'
        elif rand_direction == 'l':
            body_init1, body_init2 = (head_init[0], head_init[1] - 1), (head_init[0], head_init[1] - 2)
            self.direction = 'r'
        else:
            body_init1, body_init2 = (head_init[0], head_init[1] + 1), (head_init[0], head_init[1] + 2)
            self.direction = 'l'
        self.alive = True
        self.snake = [head_init, body_init1, body_init2]
        self.food = (randint(0, self.r_blocks - 1), randint(0, self.c_blocks - 1))
        self.score = 0
        self.update_blocks()

    def update_blocks(self):
        """
        Updates the game blocks with respect to snake and food.
        """
        for row in range(self.r_blocks):
            for block in range(self.c_blocks):
                count = (row, block)
                identity = 'empty'
                if count in self.snake:
                    if count == self.snake[0]:
                        identity = 'head'
                    else:
                        identity = 'body'
                elif count == self.food:
                    identity = 'food'
                self.blocks[row][block][1] = identity

    def draw_blocks(self):
        """
        Draws different types of blocks on to the screen.
        """
        for row in self.blocks:
            for block in row:
                color = self.blocks_color
                identity = block[1]
                is_head = False
                if identity == "head":
                    is_head = True
                    color = self.head_color
                    eye1 = pygame.Rect((block[0].x, block[0].y), (10, 10))
                    eye2 = pygame.Rect((block[0].x, block[0].y), (10, 10))
                    pygame.draw.rect(self.screen, color, block[0], border_radius=5)
                    pygame.draw.rect(self.screen, (255, 255, 255), eye1, border_radius=50)
                    pygame.draw.rect(self.screen, (255, 255, 255), eye2, border_radius=50)
                elif identity == 'body':
                    color = self.body_color
                elif identity == 'food':
                    color = self.food_color
                if not is_head:
                    pygame.draw.rect(self.screen, color, block[0], border_radius=5)
        pygame.draw.rect(self.screen, (255, 237, 218), self.board_rect, border_radius=5)
        self.screen.blit(self.score_text, self.s_pos)
        self.screen.blit(self.high_score_text, self.hs_pos)

    def _move(self, pos, state=None):
        no_state = False
        if state is None:
            no_state = True
            state = [self.snake, self.food, self.alive, False]
        if pos[0] > self.r_blocks - 1 or pos[0] < 0:
            state[2] = False
        elif pos[1] > self.c_blocks - 1 or pos[1] < 0:
            state[2] = False
        elif pos in state[0][1:]:
            state[2] = False
        else:
            if pos == state[1]:
                state[3] = True
            temp_pos = pos
            for i in range(len(state[0])):
                state[0][i], temp_pos = temp_pos, state[0][i]
        if no_state:
            if state[3]:
                print(True)
                self.grow_snake()
                self.add_food()
            self.snake = state[0]
            self.food = state[1]
            self.alive = state[2]
            self.update_blocks()
        else:
            return state

    def move(self, pos, snake_body=None):
        """
        Moves the snake to the given position.

        :param snake_body: The state of the game.
        :param pos: A tuple containing the block indexes.
        """
        if snake_body is not None:
            snake_body = snake_body.copy()
            temp_pos = pos
            for i in range(len(snake_body)):
                snake_body[i], temp_pos = temp_pos, snake_body[i]
            return snake_body
        if pos[0] > self.r_blocks - 1 or pos[0] < 0:
            self.alive = False
        elif pos[1] > self.c_blocks - 1 or pos[1] < 0:
            self.alive = False
        elif pos in self.snake[1:]:
            self.alive = False
        else:
            if pos == self.food:
                self.grow_snake()
                self.add_food()
            temp_pos = pos
            for i in range(len(self.snake)):
                self.snake[i], temp_pos = temp_pos, self.snake[i]
            self.update_blocks()

    def move_snake(self):
        """
        Moves the snake by one block in it's direction.
        """
        head = self.snake[0]
        if self.direction == 'u':
            self.move((head[0] - 1, head[1]))
        elif self.direction == 'd':
            self.move((head[0] + 1, head[1]))
        elif self.direction == 'l':
            self.move((head[0], head[1] - 1))
        else:
            self.move((head[0], head[1] + 1))
        self.moved_after_turn = True

    def turn(self, key_event, direction=None):
        """
        Turns the snake based on the key event or the specified direction.

        :param key_event: Pygame KeyEvent.key
        :param direction: The direction to turn the snake.
        """
        if not self.moved_after_turn:
            return
        if direction is None:
            if key_event == pygame.K_UP:
                direction = 'u'
            elif key_event == pygame.K_DOWN:
                direction = 'd'
            elif key_event == pygame.K_LEFT:
                direction = 'l'
            elif key_event == pygame.K_RIGHT:
                direction = 'r'
            else:
                return
        if self.direction == 'u' or self.direction == 'd':
            if direction == 'l' or direction == 'r':
                self.direction = direction
                self.moved_after_turn = False
        else:
            if direction == 'u' or direction == 'd':
                self.direction = direction
                self.moved_after_turn = False

    def update_score(self, score=1):
        self.score += score
        if self.high_score < self.score:
            self.high_score = self.score
            with open("high_score.txt", 'w') as hs:
                hs.write(str(self.high_score))
            self.high_score_text = self.font.render("High Score: " + str(self.high_score), True, self.font_color)
        self.score_text = self.font.render("Score: " + str(self.score), True, self.font_color)

    def grow_snake(self):
        """
        Increases the length of snake by one block.
        """
        head_pos = self.snake[0]
        if self.direction == 'u':
            body = (head_pos[0] - 1, head_pos[1])
        elif self.direction == 'd':
            body = (head_pos[0] + 1, head_pos[1])
        elif self.direction == 'l':
            body = (head_pos[0], head_pos[1] - 1)
        else:
            body = (head_pos[0], head_pos[1] + 1)
        self.snake.append(body)
        self.update_score()

    def add_food(self):
        """
        Adds food on a random block without snake.
        """
        food_blocks = []
        for row in range(1, self.r_blocks - 1):
            for col in range(1, self.c_blocks - 1):
                if (row, col) not in self.snake:
                    food_blocks.append((row, col))
        self.food = choice(food_blocks)

    def next_states(self, snake_body: list) -> list:
        """"
        Returns the list of next possible snake positions.
        :param snake_body: The list containing the body positions of each block of snake.
        :return: The list of next possible snake positions.
        """
        head_x, head_y = snake_body[0][0], snake_body[0][1]
        surrounding_blocks = [(head_x + 1, head_y), (head_x - 1, head_y), (head_x, head_y + 1), (head_x, head_y - 1)]
        next_blocks = []
        for i in range(len(surrounding_blocks)):
            if surrounding_blocks[i] in snake_body:
                pass
            elif surrounding_blocks[i][0] < 0 or surrounding_blocks[i][0] >= self.r_blocks:
                pass
            elif surrounding_blocks[i][1] < 0 or surrounding_blocks[i][1] >= self.c_blocks:
                pass
            else:
                next_blocks.append(surrounding_blocks[i])
        next_states = []
        if len(next_blocks) != 0:
            for pos in next_blocks:
                snake_body = snake_body.copy()
                temp_pos = pos
                for i in range(len(snake_body)):
                    snake_body[i], temp_pos = temp_pos, snake_body[i]
                next_states.append(snake_body)
        return next_states

    def at_food(self, snake_body: list) -> bool:
        return snake_body[0] == self.food

    def _next_states(self, state):
        head_x, head_y = state[0], state[1]
        surrounding_blocks = [(head_x + 1, head_y), (head_x - 1, head_y), (head_x, head_y + 1), (head_x, head_y - 1)]
        next_blocks = []
        for i in range(len(surrounding_blocks)):
            if surrounding_blocks[i] in self.snake:
                pass
            elif surrounding_blocks[i][0] < 0 or surrounding_blocks[i][0] >= self.r_blocks:
                pass
            elif surrounding_blocks[i][1] < 0 or surrounding_blocks[i][1] >= self.c_blocks:
                pass
            else:
                next_blocks.append(surrounding_blocks[i])

        return next_blocks

    def _at_food(self, pos):
        return pos == self.food

    def solve(self):
        try:
            search = Search(goal_test=self._at_food, next_states=self._next_states, state=self.snake[0])
            path = search.search(algorithm='bfs', verbose=False, show_time=False)
            for state in path:
                self.move(state)
                self.update_blocks()
                self.draw_blocks()
                pygame.display.update()
            search.tree = {}
        except StopIteration:
            self.reset()
            # # self.move(choice(self._next_states(self.snake[0])))
            # search = Search(goal_test=self.at_food, next_states=self.next_states, state=self.snake)
            # path = search.search(algorithm='bfs')
            # for state in path:
            #     self.snake = state
            #     self.update_blocks()
            #     self.draw_blocks()
            #     pygame.display.update()
            # self.grow_snake()
            # self.update_blocks()
            # self.draw_blocks()
            # self.add_food()
            # # search.tree = {}

    def main(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(3)
            self.screen.fill(self.bg_color)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_SPACE:
                        if self.pause:
                            self.pause = False
                        else:
                            self.pause = True
                    elif not self.pause:
                        self.turn(event.key)
            self.solve()
            self.update_blocks()
            self.draw_blocks()
            pygame.display.update()


if __name__ == '__main__':
    Snake(r_blocks=30, c_blocks=65)
