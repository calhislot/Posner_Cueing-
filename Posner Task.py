import pygame
import random
import time
import csv
import os
import pandas as pd
from scipy import stats 

# Pygame Initialization
pygame.init()

# Screen Settings (Fullscreen)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

# Colours
colours = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'grey': (211, 211, 211),
    'red': (255, 0, 0)
}

# Key Mapping
key_mapping = {'left': pygame.K_q, 'right': pygame.K_p}

# Fonts
font_name = 'Arial'
font = pygame.font.SysFont(font_name, 30, bold=True)

# Data Storage
data_file = 'posner_experiment_data.csv'

# Experiment Variables
num_practice_trials = 10
num_real_trials = 10

# Participant Name Input
def get_participant_name():
    name = ""
    input_active = True
    while input_active:
        screen.fill(colours['white'])
        prompt = font.render("Please enter your name: " + name, True, colours['black'])
        screen.blit(prompt, (WIDTH//2 - 200, HEIGHT//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                else:
                    name += event.unicode
    return name

# Display Instructions
def show_instructions():
    screen.fill(colours['white'])

    title_font = pygame.font.SysFont(font_name, 50)
    body_font = pygame.font.SysFont(font_name, 30)

    instructions = [
        "Welcome to the Posner Cueing Task!",
        "Two black squares will appear on either side of the fixation cross.",
        "Please make sure to stay focused on the cross in the middle of the screen.",
        "The cue will shade one of the squares grey.",
        "Immediately following this, a red circle will appear in one of the squares",
        "Press Q if the circle appears on the LEFT.",
        "Press P if the circle appears on the RIGHT.",
        "Press SPACE to begin practice trials."
    ]

    title_y = HEIGHT // 4

    title_text = title_font.render(instructions[0], True, colours['black'])
    title_rect = title_text.get_rect(center=(WIDTH //2, title_y))
    screen.blit(title_text, title_rect.topleft)

    start_y = title_y + 80

    for i, line in enumerate(instructions[1:]):
        text = body_font.render(line, True, colours['black'])
        text_rect = text.get_rect(center=(WIDTH // 2, start_y + i * 40))
        screen.blit(text, text_rect.topleft)
    pygame.display.flip()
    wait_for_space()

# Wait for Space Key
def wait_for_space():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# Run a Block of Trials
def run_trials(num_trials, practice=False):
    results = []
    trial_types = ['congruent'] * (num_trials // 2) + ['incongruent'] * (num_trials // 2)
    random.shuffle(trial_types)
    
    for trial_type in trial_types:
        cue_side = random.choice(['left', 'right'])
        target_side = cue_side if trial_type == 'congruent' else ('left' if cue_side == 'right' else 'right')
        reaction_time, response = run_trial(cue_side, target_side)
        congruent = cue_side == target_side
        correct = response == target_side
        results.append([cue_side, target_side, congruent, reaction_time, correct])
    return results

# Run a Single Trial
def run_trial(cue_side, target_side):
    screen.fill(colours['white'])
    
    # Draw squares 
    left_square = pygame.draw.rect(screen, colours['black'], (WIDTH//4, HEIGHT//2 - 50, 100, 100), 3)
    right_square = pygame.draw.rect(screen, colours['black'], (3 * WIDTH//4 - 100, HEIGHT//2 - 50, 100, 100), 3)
    
    # Draw fixation cross
    pygame.draw.line(screen, colours['black'], (WIDTH//2 - 10, HEIGHT//2), (WIDTH//2 + 10, HEIGHT//2), 3)
    pygame.draw.line(screen, colours['black'], (WIDTH//2, HEIGHT//2 - 10), (WIDTH//2, HEIGHT//2 + 10), 3)
    pygame.display.flip()
    time.sleep(1)

    # Display cue as filled grey square
    cue_x = WIDTH//4 if cue_side == 'left' else 3 * WIDTH//4 - 100
    pygame.draw.rect(screen, colours['grey'], (cue_x, HEIGHT//2 - 50, 100, 100))
    pygame.display.flip()
    time.sleep(0.5)

    # Display target as a red circle
    target_pos = (WIDTH//4 + 50, HEIGHT//2) if target_side == 'left' else (3 * WIDTH//4 - 50, HEIGHT//2)
    pygame.draw.circle(screen, colours['red'], target_pos, 20)
    pygame.display.flip()
    start_time = time.time()

    # Wait for response
    response = None
    while response is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key in key_mapping.values():
                    reaction_time = time.time() - start_time
                    response = 'left' if event.key == key_mapping['left'] else 'right'
                    return reaction_time, response

# Save Data
def save_data(participant_name, trial_data):
    file_exists = os.path.isfile(data_file)
    with open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Participant', 'Cue Side', 'Target Side', 'Congruent', 'Reaction Time', 'Correct/Incorrect Response'])
        for row in trial_data:
            writer.writerow([participant_name] + row)

# Main Experiment Routine
participant_name = get_participant_name()
show_instructions()
practice_results = run_trials(num_practice_trials, practice=True)

# Post-practice message
screen.fill(colours['white'])
text = font.render("The Practice Trials Are Over. Please Press SPACE To Begin The Test Trials.", True, colours['black'])
text_rect = text.get_rect(center=(WIDTH //2, HEIGHT //2))
screen.blit(text, text_rect.topleft)
pygame.display.flip()
wait_for_space()

# Real trials
real_results = run_trials(num_real_trials, practice=False)
save_data(participant_name, real_results)

# End message
screen.fill(colours['white'])
text = font.render("Thank You For Completing Our Experiment! Press Any Key to Exit.", True, colours['black'])
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(text, text_rect.topleft)
pygame.display.flip()
wait_for_space()


pygame.quit()


