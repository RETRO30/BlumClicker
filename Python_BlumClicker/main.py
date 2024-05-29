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
import threading





def detect_first_green_object(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)
            return (cx, cy), image

    return None, image

def show_image(image):
    cv2.imshow("Hello world", image)
    cv2.waitKey(1)

def wait_for_enter():
    input("Press Enter to continue...")
    
    
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
        self.c_pos_x = 0
        self.c_pos_y = 0
        self.html_element =None
    
    
    def get_page_screenshot(self, isTest=False):
        screenshot = self.driver.get_screenshot_as_png()
        
        image = Image.open(io.BytesIO(screenshot))
        
        cropped_image = image.crop((self.frame_x, self.frame_y, self.frame_x+self.frame_width, self.frame_y+self.frame_height-50))
    
        cropped_image_np = np.array(cropped_image)
        
        if isTest:
            cropped_image.save("test.png")
        
        return cropped_image_np
    
    def click_at_coordinates(self, x, y):
        print("Clicking at", x, y)
        
        ActionChains(self.driver, 1).move_to_element_with_offset(self.html_element, -self.frame_width/2, -self.frame_height/2).perform()

        # Переместите курсор к заданным координатам и кликните
        ActionChains(self.driver, 1).move_by_offset(x, y).click().perform()
    
    def setup(self):
        chrome_options = Options()
        chrome_options.add_argument('proxy-server=http://127.0.0.1:8080')
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
            self.html_element = self.driver.find_element(By.TAG_NAME, 'html')
        else:
            exit(0)
        print("Frame location:", self.frame_x, self.frame_y, self.frame_width, self.frame_height)   
        print("Press play...")
        
        WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.play-btn'))
                ).click()
        
        print("Game started")
        
            
        
    
    def get_window_size(self):
        window_size_script = "return [window.innerWidth, window.innerHeight];"
        return self.driver.execute_script(window_size_script)
    
    def update(self):
        if self.get_window_size() != [self.window_width, self.window_height]:
            self.driver.set_window_size(self.window_width, self.window_height)
            self.driver.set_window_position(0, 0)
        try:
            image = self.get_page_screenshot()
            centers, image = detect_first_green_object(image)
            show_image(image)
            if centers is not None:
                if centers[0] >= self.frame_width and centers[1] >= self.frame_height:
                    print("Out of bounds")
                else:
                    self.click_at_coordinates(centers[0], centers[1])
            else:
                print("No objects found")
        except Exception as e:
            print(e)
        
        
    def input(self):
        if keyboard.is_pressed("q"):
            exit(0)
        
    def run(self):
        self.setup()
        while True:
            self.input()
            self.update()


def main():
    app = BlumClicker()
    app.run()
    
def test():
    image = cv2.imread("test.png")
    centers, image = detect_in_area(image)
    cv2.imshow("Hello world", image)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
