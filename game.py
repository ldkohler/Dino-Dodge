"""
-----======= [ Dino Dodge Project Explanation ] =======-----

Our game will be called Dino Dodge.

Description:
In our game the player will be a dinosaur that runs side to side at the bottom of the display. The goal of the player is
to avoid the meteors falling from the sky by dodging them. There will be several waves that increase in difficulty.
Waves become more difficult based on the spawn frequency, speed, duration, and total lives allowed to the player in
each wave. Finally, the player wins by completing the final wave without running out of lives, and the player loses if
they run out of lives before the end of the current wave.

---- Basic Features ----

User Input:
The player will be able to move horizontally side to side using the left and right arrow keys.
We will implement this through a function that handles player movement which checks for keyboard input and moves the
player's x position accordingly.

Game Over:
The game will end when the player runs out of lives. The player will lose one life for each meteor that hits them.
For each wave, the amount of lives resets and increases with difficulty.

Graphics/Images:
For the player, we will make a custom animated spite. For each meteor we will also include a custom-made sprite.
Finally, the background will not simply be a solid color, but we will design one that looks like the sky.

---- Additional Features ----

Restart from Game Over:
When the player is out of lives and the game ends, we will allow the player to restart the game by pressing the [r] key.
This will place the player back at wave 1 and reset the score. We will implement this in a function that handles an end
state menu and a boolean that tracks game running progress.

Sprite Animation:
The player sprite will be an animated dinosaur that walks side to side. To implement this feature, we will design a
custom sprite sheet that contains several frames of a pixel art dino walking. Then we will loop through the sprite
sheet and flip the images depending on in which direction the player is moving.

Collectibles:
The player will have the opportunity to collect extra lives in the form of a collectible heart sprite. Collectibles will
be spawned at random intervals and there will be a limited number per wave. Once a player touches a heart collectible
their lives will be increased by one.

Timer:
There will be a timer on display that counts the amount of seconds left before the wave is over.
By using an accumulator, we can subtract (1 / frame rate) for each tick to achieve a basic countdown clock. Once the timer
reaches 0, we move progress the game to the next wave.

Multiple Levels:
There will be a series of waves that progressively get more difficult as the player successfully progresses. We will
store each wave and its associated settings (duration, lives, meteor speed, etc) in a list of dictionaries which we will
access when we begin a new wave via a function.
"""

import uvage
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
tick_rate = 60
camera = uvage.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

wave_clock = 0
meteor_spawn_clock = 0
collectable_spawn_clock = 0
frame = 0
score = 0
current_lives = 1
current_wave = 0

health_bar_images = uvage.load_sprite_sheet("healthbar.png", rows=9, columns=1)
dino_images = uvage.load_sprite_sheet("dino.png", rows=1, columns=4)

health_bar = uvage.from_image(SCREEN_WIDTH / 2, 750, health_bar_images[0])
player = uvage.from_image(100, 100, dino_images[0])
ground = uvage.from_image(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50, "ground.png")
background = uvage.from_image(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "background.png")


is_running = False
player_won = False
player_lost = False
facing_right = False

meteors = []
collectables = []
waves = [{"spawn_interval": 0.425, "min_speed": 4, "max_speed": 7, "duration": 30, "max_collectables": 1},
        {"spawn_interval": 0.25, "min_speed": 7, "max_speed": 12, "duration": 30, "max_collectables": 2},
        {"spawn_interval": 0.175, "min_speed": 10, "max_speed": 15, "duration": 30, "max_collectables": 5},
        {"spawn_interval": 0.25, "min_speed": 15, "max_speed": 20, "duration": 30, "max_collectables": 5}]


def spawn_meteor(wave):
    global meteors
    x_pos = random.randrange(0, SCREEN_WIDTH)
    y_pos = -60
    scale = random.uniform(0.4, 1.5)
    speed = random.randrange(wave["min_speed"], wave["max_speed"])
    meteor = uvage.from_image(x_pos, y_pos, "meteor.png")
    meteor.scale_by(scale)
    meteors.append([meteor, speed])


def spawn_collectable():
    global collectables
    x_pos = random.randrange(0, SCREEN_WIDTH)
    y_pos = -60
    collectable = uvage.from_image(x_pos, y_pos, "collectable.png")
    collectables.append(collectable)


def clear_meteors():
    global meteors, meteor_spawn_clock
    meteors = []
    meteor_spawn_clock = 0


def clear_collectables():
    global collectables, collectable_spawn_clock
    collectables = []
    collectable_spawn_clock = 0


def play_wave(wave):
    global meteor_spawn_clock, meteors, collectable_spawn_clock, collectables
    meteor_spawn_clock += 1 / tick_rate
    if meteor_spawn_clock >= wave["spawn_interval"]:
        meteor_spawn_clock = 0
        spawn_meteor(wave)
    collectable_spawn_clock += 1 / tick_rate
    if wave["max_collectables"] == 1 and collectable_spawn_clock >= wave["duration"] / 2 and current_lives < 9:
        collectable_spawn_clock = 0
        spawn_collectable()
    elif wave["max_collectables"] > 1 and collectable_spawn_clock >= (wave["duration"] - 5) / wave["max_collectables"] and current_lives < 9:
        collectable_spawn_clock = 0
        spawn_collectable()
    for meteor in meteors:
        meteor[0].y += meteor[1]
        if meteor[0].y >= SCREEN_HEIGHT + 200:
            meteors.remove(meteor)
    for collectable in collectables:
        collectable.y += 4
        if collectable.y >= SCREEN_HEIGHT + 200:
            collectables.remove(collectable)


def cycle_waves():
    global waves, wave_clock, current_wave, player_won, is_running, player, score
    wave_clock += 1 / tick_rate
    if wave_clock <= waves[current_wave]["duration"]:
        play_wave(waves[current_wave])
    elif wave_clock <= waves[current_wave]["duration"] + 3:
        if current_wave == (len(waves) - 1):
            is_running = False
            player_won = True
            score += 100
        else:
            camera.clear("black")
            camera.draw("Wave " + str(current_wave + 1) + " of " + str(len(waves)) + " complete!", 50, "white",
                        SCREEN_WIDTH / 2, 150)
            camera.draw("Next wave starting in:", 50, "white", SCREEN_WIDTH / 2, 200)
            camera.draw(str(abs(int(wave_clock) - (waves[current_wave]["duration"] + 3))), 150, "white",
                        SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            camera.draw("+100 pts!", 75, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 200)
            camera.draw("Score: " + str(score + 100), 50, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150)
            clear_meteors()
            clear_collectables()
    else:
        camera.clear("black")
        wave_clock = 0
        score += 100
        clear_meteors()
        clear_collectables()
        player.x = SCREEN_WIDTH / 2
        player.y = SCREEN_HEIGHT - 150
        current_wave += 1


def handle_player():
    global player, is_running, player_lost, meteors, current_lives, score, collectables, facing_right, frame
    player_speed = 5
    is_moving = False
    if uvage.is_pressing("right arrow") or uvage.is_pressing("d"):
        if player.x <= SCREEN_WIDTH:
            player.x += player_speed
            is_moving = True
            if not facing_right:
                facing_right = True
                player.flip()
    if uvage.is_pressing("left arrow") or uvage.is_pressing("a"):
        if player.x >= 0:
            player.x += -player_speed
            is_moving = True
            if facing_right:
                facing_right = False
                player.flip()
    player.speedy += 1
    if player.touches(ground):
        player.speedy = 0
        player.move_to_stop_overlapping(ground)
        if uvage.is_pressing("space") or uvage.is_pressing("up arrow") or uvage.is_pressing("w"):
            player.speedy = - 10
    else:
        is_moving = True
    player.move_speed()
    if not is_moving:
        player.image = dino_images[0]
    elif player.touches(ground):
        frame += 10 / tick_rate
        if frame > 3:
            frame = 0
        player.image = dino_images[int(frame)]
    elif not player.touches(ground):
        player.image = dino_images[3]
    for meteor in meteors:
        if player.touches(meteor[0]):
            current_lives -= 1
            camera.clear("red")
            meteors.remove(meteor)
            score -= 10
            if current_lives <= 0:
                is_running = False
                player_lost = True
    for collectable in collectables:
        if player.touches(collectable):
            collectables.remove(collectable)
            score += 25
            current_lives += 1


def reset_game():
    global player_won, player_lost, current_lives, wave_clock, meteor_spawn_clock, collectable_spawn_clock, current_wave, player, score
    current_wave = 0
    wave_clock = 0
    score = 0
    current_lives = 1
    player_lost = False
    player_won = False
    clear_meteors()
    clear_collectables()
    player.x = SCREEN_WIDTH / 2
    player.y = SCREEN_HEIGHT - 150


def handle_health_bar():
    global health_bar
    health_bar.image = health_bar_images[current_lives - 1]


def tick():
    global is_running, score
    camera.clear("black")
    if uvage.is_pressing("return") and not is_running:
        reset_game()
        is_running = True
    if is_running:
        camera.draw(background)
        if abs(int(wave_clock) - (waves[current_wave]["duration"])) <= 3:
            camera.draw(str(abs(int(wave_clock) - (waves[current_wave]["duration"]))), 150, "white",
                        SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        for meteor in meteors:
            camera.draw(meteor[0])
        for collectable in collectables:
            camera.draw(collectable)
        camera.draw(ground)
        if int(waves[current_wave]["duration"] - wave_clock) > 1:
            camera.draw((str(int(waves[current_wave]["duration"] - wave_clock + 1))) + " seconds left", 35, "white",
                        SCREEN_WIDTH / 2, 80)
        elif int(waves[current_wave]["duration"] - wave_clock) == 1:
            camera.draw((str(int(waves[current_wave]["duration"] - wave_clock + 1))) + " second left", 35, "white",
                        SCREEN_WIDTH / 2, 80)
        elif int(waves[current_wave]["duration"] - wave_clock) == 0:
            camera.draw((str(int(waves[current_wave]["duration"] - wave_clock + 1))) + " seconds left", 35, "white",
                        SCREEN_WIDTH / 2, 80)
        camera.draw("Wave: " + str(current_wave + 1) + "/" + str(len(waves)) + "  |  " + "Score: " + str(score), 35,
                    "white", SCREEN_WIDTH / 2, 50)
        handle_player()
        camera.draw(player)
        handle_health_bar()
        camera.draw(health_bar)
        cycle_waves()
    elif player_won:
        camera.clear("dark green")
        camera.draw("YOU SURVIVED", 100, "white", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        camera.draw("+100 pts!", 75, "yellow", SCREEN_WIDTH / 2, 200)
        camera.draw("Final Score: " + str(score), 50, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)
    elif player_lost:
        camera.clear("dark red")
        camera.draw("YOU DIED", 100, "white", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        camera.draw("Final Score: " + str(score), 50, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)
    if not is_running:
        camera.draw("Press [RETURN] To Play", 50, "white", SCREEN_WIDTH / 2, 50)
    camera.display()


uvage.timer_loop(tick_rate, tick)
