import cv2
import mediapipe as mp
import pygame
import math

WIDTH = 900
HEIGHT = 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Controlled Fractal Tree")

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1) 
mpDraw = mp.solutions.drawing_utils

class Tree:
    def __init__(self, x, y, size, decay, tilt_amount, bias_amount):
        self.x = x
        self.y = y
        self.size = size
        self.decay = decay
        self.tilt_amount = math.radians(tilt_amount)
        self.bias_amount = math.radians(bias_amount)

    def draw_branch(self, length, x, y, angle, bias, depth=0):
        if length > 1:
            x1, y1 = get_next_point(x, y, angle + self.tilt_amount + bias, length)
            x2, y2 = get_next_point(x, y, angle - self.tilt_amount + bias, length)
            pygame.draw.line(win, (255, 255, 255), (x, y), (x1, y1))
            pygame.draw.line(win, (255, 255, 255), (x, y), (x2, y2))
            
            if depth < 10:  
                self.draw_branch(length * self.decay, x1, y1, angle + self.tilt_amount, bias + self.bias_amount, depth + 1)
                self.draw_branch(length * self.decay, x2, y2, angle - self.tilt_amount, bias + self.bias_amount, depth + 1)
        else:
            print(f"Stopping recursion at length: {length}, depth: {depth}")

    def draw(self):
        pygame.draw.line(win, (255, 255, 255), (self.x, self.y), (self.x, self.y + self.size))
        self.draw_branch(self.size, self.x, self.y, math.radians(180), 0)

def get_next_point(x, y, angle, length):
    x2 = x + math.sin(angle) * length
    y2 = y + math.cos(angle) * length
    return x2, y2

def mean(data):
    return sum(data) / len(data)

def map_range(value, in_min, in_max, out_min, out_max):
    in_range = in_max - in_min
    out_range = out_max - out_min
    percent_done = (value - in_min) / in_range
    return out_range * percent_done + out_min

def get_hand_location(img):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        x_values = []
        y_values = []
        for hand in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)
            for landmark in hand.landmark:
                height, width, _ = img.shape
                centerx, centery = int(landmark.x * width), int(landmark.y * height)
                x_values.append(centerx)
                y_values.append(centery)
        meanx = int(mean(x_values))
        meany = int(mean(y_values))
        return meanx, meany
    return None

def update(trees, mousepos, img):
    win.fill((32, 32, 32))
    for tree in trees:
        tree.tilt_amount = math.radians(map_range(mousepos[0], 0, WIDTH, 0, 90))
        tree.bias_amount = math.radians(map_range(mousepos[1], 0, HEIGHT, 0, 90))
        tree.draw()
    pygame.display.flip()

    flipped = cv2.flip(img, 1)
    cv2.imshow("Image", flipped)

def main():
    trees = [Tree(WIDTH // 2, HEIGHT - 200, 200, 0.65, 90, 20)]
    prev_hand_location = (WIDTH // 2, HEIGHT // 2)

    run = True
    clock = pygame.time.Clock()

    while run:
        success, img = cap.read()
        if not success:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        hand_location = get_hand_location(img)
        if hand_location:
            prev_hand_location = hand_location

        update(trees, prev_hand_location, img)
        clock.tick(60)  
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
