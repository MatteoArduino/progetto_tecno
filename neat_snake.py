import pygame
import random
import sys
import neat
import time


pygame.init()


WIDTH, HEIGHT = 640, 480
CELL_SIZE = 20


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


font = pygame.font.SysFont(None, 48)


apple_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
apple_img.fill((255, 0, 0))  # Red apple
grass_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
grass_img.fill((0, 255, 0))  # Green grass
head_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
head_img.fill((0, 0, 255))  # Blue snake head
tail_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
tail_img.fill((0, 255, 255))  # Cyan snake tail

# configuro la schermata di gioco
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')


clock = pygame.time.Clock()


DIRECTIONS = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}

class Snake:
    def __init__(self):
        self.body = [(5, 5), (5, 6), (5, 7)]
        self.direction = 'up'
        self.new_direction = self.direction
        self.score = 0  # Score variable
        self.last_eat_time = time.time()
    
    def move(self):
        self.direction = self.new_direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = DIRECTIONS[self.direction]
        new_head = (head_x + dir_x, head_y + dir_y)

        #controllo se lo snake colpisce il muro
        if new_head[0] < 0 or new_head[0] >= WIDTH // CELL_SIZE or \
           new_head[1] < 0 or new_head[1] >= HEIGHT // CELL_SIZE:
            
            return True

        #controllo se lo snake colpisce un pezzo del suo corpo
        if new_head in self.body:
            return True

        
        self.body = [new_head] + self.body[:-1]

        return False

    def grow(self):
        self.body.append(self.body[-1])
        self.score += 1  
        self.last_eat_time = time.time()  

    def change_direction(self, direction):
        opposite_directions = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left'
        }
        if direction != opposite_directions[self.direction]:
            self.new_direction = direction

    def check_collision(self):
        head = self.body[0]
        return head in self.body[1:]

class Apple:
    def __init__(self):
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, WIDTH // CELL_SIZE - 1), random.randint(0, HEIGHT // CELL_SIZE - 1))

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, HEIGHT, CELL_SIZE):
            screen.blit(grass_img, (x, y))

def draw_snake(snake):
    for i, (x, y) in enumerate(snake.body):
        if i == 0:  
            screen.blit(head_img, (x * CELL_SIZE, y * CELL_SIZE))
        else:
            screen.blit(tail_img, (x * CELL_SIZE, y * CELL_SIZE))

def draw_score(score):
    score_text = f'Score: {score}'
    draw_text(score_text, (10, 10))  

def draw_apple(apple):
    apple_x, apple_y = apple.position
    screen.blit(apple_img, (apple_x * CELL_SIZE, apple_y * CELL_SIZE))

def draw_text(text, position, center=False):
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = position
    else:
        text_rect.topleft = position
    screen.blit(text_surface, text_rect.topleft)

def show_start_screen():
    screen.fill(BLACK)
    draw_text('Snake Game', (WIDTH // 2, HEIGHT // 4), center=True)
    draw_text('Press any key to start', (WIDTH // 2, HEIGHT // 2), center=True)
    pygame.display.update()
    wait_for_key()

def show_game_over_screen():
    screen.fill(BLACK)
    draw_text('Game Over', (WIDTH // 2, HEIGHT // 4), center=True)
    draw_text('Press any key to restart', (WIDTH // 2, HEIGHT // 2), center=True)
    pygame.display.update()
    wait_for_key()

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def get_inputs(snake, apple):
    head_x, head_y = snake.body[0]
    apple_x, apple_y = apple.position

    def cell_is_free(x, y):
        return 0 <= x < WIDTH // CELL_SIZE and 0 <= y < HEIGHT // CELL_SIZE and (x, y) not in snake.body

    def distance_to_obstacle(dx, dy):
        x, y = head_x, head_y
        distance = 0
        while cell_is_free(x + dx, y + dy):
            x += dx
            y += dy
            distance += 1
        return distance

    distance_to_wall_up = head_y
    distance_to_wall_down = (HEIGHT // CELL_SIZE) - head_y - 1
    distance_to_wall_left = head_x
    distance_to_wall_right = (WIDTH // CELL_SIZE) - head_x - 1

    
    distance_to_apple = abs(head_x - apple_x) + abs(head_y - apple_y)
    max_distance = (WIDTH // CELL_SIZE) + (HEIGHT // CELL_SIZE)
    normalized_distance_to_apple = distance_to_apple / max_distance

    input_data = [
        head_x / (WIDTH // CELL_SIZE),  
        head_y / (HEIGHT // CELL_SIZE),  
        apple_x / (WIDTH // CELL_SIZE),  
        apple_y / (HEIGHT // CELL_SIZE), 
        int(cell_is_free(head_x, head_y - 1)), 
        int(cell_is_free(head_x, head_y + 1)), 
        int(cell_is_free(head_x - 1, head_y)), 
        int(cell_is_free(head_x + 1, head_y)),  
        distance_to_wall_up / (HEIGHT // CELL_SIZE),  
        distance_to_wall_down / (HEIGHT // CELL_SIZE),  
        distance_to_wall_left / (WIDTH // CELL_SIZE),  
        distance_to_wall_right / (WIDTH // CELL_SIZE),  
        distance_to_obstacle(0, -1) / (HEIGHT // CELL_SIZE),
        distance_to_obstacle(0, 1) / (HEIGHT // CELL_SIZE), 
        distance_to_obstacle(-1, 0) / (WIDTH // CELL_SIZE),  
        distance_to_obstacle(1, 0) / (WIDTH // CELL_SIZE),
        normalized_distance_to_apple  
    ]
    
    return input_data



def evaluate_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        snake = Snake()
        apple = Apple()

        genome.fitness = 0  # Initialize fitness score

        steps_without_eating = 0
        while True:
            input_data = get_inputs(snake, apple)
            output = net.activate(input_data)
            direction_index = output.index(max(output))

            # Validate direction to ensure it's a legal move
            if direction_index == 0:
                direction = 'up'
            elif direction_index == 1:
                direction = 'down'
            elif direction_index == 2:
                direction = 'left'
            elif direction_index == 3:
                direction = 'right'
            else:
                direction = snake.direction  # If invalid, keep the current direction

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            snake.change_direction(direction)
            if snake.move():
                genome.fitness -= 10  # Penalize heavily for hitting the wall or itself
                break

            if snake.body[0] == apple.position:
                snake.grow()
                apple.randomize_position()
                genome.fitness += 10  # Increase fitness score when snake eats an apple
                steps_without_eating = 0
            else:
                steps_without_eating += 1

                # Penalize for not eating for too long
                if steps_without_eating > 10:
                    genome.fitness -= 5
                    break

            # Reward the genome for each step it stays alive
            genome.fitness += 0.1

            # Additional reward for moving towards the apple
            head_x, head_y = snake.body[0]
            apple_x, apple_y = apple.position
            current_distance = abs(head_x - apple_x) + abs(head_y - apple_y)
            next_distance = abs(head_x + DIRECTIONS[direction][0] - apple_x) + abs(head_y + DIRECTIONS[direction][1] - apple_y)
            if next_distance < current_distance:
                genome.fitness += 0.5  # Reward for moving towards the apple
            else:
                genome.fitness -= 0.5  # Penalize for moving away from the apple

            screen.fill(BLACK)
            draw_grid()
            draw_snake(snake)
            draw_apple(apple)
            draw_score(snake.score)
            pygame.display.flip()
            clock.tick(10)


def main():
    show_start_screen()

    # Load NEAT configuration from the config file
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config.txt')

    # Create the genome pool using NEAT configuration
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run population evolution and get the best genome
    winner = p.run(evaluate_genomes, 50)

    # Run the game with the neural network of the best genome
    evaluate_genomes([(1, winner)], config)

if __name__ == '__main__':
    main()
