import keyboard
import selenium.webdriver as webdriver
import numpy as np
import cv2
from PIL import Image
import io
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def detect_green_objects(image, min_neighbors=5):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (40, 40, 40), (80, 255, 255))
    filtered_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(filtered_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    centers = []

    for contour in contours:
        if cv2.contourArea(contour) < 100:
            continue

        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            centers.append((cx, cy))
            cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 3)
            return image, centers

    return image, centers


def show_image(image):
    cv2.imshow("Hello world", image)
    cv2.waitKey(1)


def move_mouse_to(x, y):
    pyautogui.moveTo(x, y, duration=0.25, tween=pyautogui.easeInOutQuad)


def wait_for_enter():
    input("Press Enter to continue...")


def setup():
    driver = webdriver.Chrome()
    url = "https://web.telegram.org/k/"
    driver.get(url)
    print("Waiting for setup... Login, open web app and press enter")
    input()
    print("Press play...")
    
    
class BlumClicker:
    def __init__(self):
        self.driver = None
        self.url = "https://web.telegram.org/k/"
        self.window_width = 500
        self.window_height = 1000
        self.frame_x = 0
        self.frame_y = 0
        self.frame_width = 0
        self.frame_height = 0
        self.game_frame = None
        self.game_canvas = None
    
    
    def get_page_screenshot(self, isTest=False):
        screenshot = self.driver.get_screenshot_as_png()
        
        image = Image.open(io.BytesIO(screenshot))
        
        cropped_image = image.crop((self.frame_x, self.frame_y, self.frame_x+self.frame_width, self.frame_y+self.frame_height))
    
        cropped_image_np = np.array(cropped_image)
        
        if isTest:
            cropped_image.save("test.png")
        
        return cropped_image_np
    
    def click_at_coordinates(self, x, y):
        action = ActionChains(self.driver)
        action.move_by_offset(x, y).click().perform()
        
    def click_at_game(self, x, y):
        self.click_at_coordinates(x + self.frame_x, y + self.frame_y)
        
    def setup(self):
        chrome_options = Options()
        chrome_options.add_argument('--log-level=3')  
        self.driver = webdriver.Chrome(chrome_options)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(self.window_width, self.window_height)
        self.driver.get(self.url)
        print("Waiting for setup... Login, open web app and press enter")
        input()

        
        while self.game_frame == None:
            print("Finding popup frame...")
            try:
                self.game_frame = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe'))
                )
            except Exception as e:
                self.game_frame = None
                sleep(0.1)
        if self.game_frame != None:
            print("Game frame found")
            self.frame_x = self.game_frame.location['x']
            self.frame_y = self.game_frame.location['y']
            self.frame_width = self.game_frame.size['width']
            self.frame_height = self.game_frame.size['height']
            self.driver.switch_to.frame(self.game_frame)
        else:
            exit(0)
            
            
        while self.game_canvas == None:
            print("Finding game canvas...")
            try:
                self.game_canvas = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas[width="420"]'))
                )
            except Exception as e:
                self.game_canvas = None
                sleep(0.1)
        print("Game canvas found")
        
        print("Press play...")
        
        
        while self.game_canvas.get_attribute("style") == "display: none;":
            self.game_canvas = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas[width="420"]'))
            )        
        
        print("Game started")
        
            
        
    
    def get_window_size(self):
        window_size_script = "return [window.innerWidth, window.innerHeight];"
        return self.driver.execute_script(window_size_script)
    
    def update(self):
        if self.get_window_size() != [self.window_width, self.window_height]:
            self.driver.set_window_size(self.window_width, self.window_height)
            self.driver.set_window_position(0, 0)
            
        image = self.get_page_screenshot()
        image, centers = detect_green_objects(image)
        show_image(image)
        if len(centers) > 0:
            self.click_at_game(centers[0][0], centers[0][1])
            print("Clicked at", centers[0][0], centers[0][1])
        else:
            print("No objects found")
        
        
    def input(self):
        if keyboard.is_pressed("q"):
            exit(0)
        
    def run(self):
        self.setup()
        while True:
            self.input()
            self.update()
            sleep(0.0001)


def main():
    app = BlumClicker()
    app.run()


if __name__ == "__main__":
    main()
