class Keypad:
    # Initialize the keypad class
    def __init__(self,
                 rows=[29, 31, 33, 35],
                 columns=[32, 36, 38, 40],
                 key_labels=[
                     ['1', '2', '3', 'A'],
                     ['4', '5', '6', 'B'],
                     ['7', '8', '9', 'C'],
                     ['*', '0', '#', 'D']
                 ],
                 ret_char='D'):
        import RPi.GPIO as GPIO

        # Initialize rows, columns, key labels and return char
        self.rows = rows
        self.columns = columns
        self.key_labels = key_labels
        self.ret_char = ret_char
        # set up the GPIO Numbering Mode To Board (Position of the Pin on The Board)
        GPIO.setmode(GPIO.BOARD)
        # set the keypad pins
        for row in rows:
            GPIO.setup(row, GPIO.OUT)
        for column in columns:
            GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # function to read the keypad
    def read_keypad(self):
        from time import sleep
        import RPi.GPIO as GPIO
        key_strokes = ''
        no_press = True
        no_press_old = True
        while True:
            no_press = True
            for my_row in [0, 1, 2, 3]:
                for my_column in [0, 1, 2, 3]:
                    GPIO.output(self.rows[my_row], GPIO.HIGH)
                    button_value = GPIO.input(self.columns[my_column])
                    GPIO.output(self.rows[my_row], GPIO.LOW)
                    if button_value == 1:
                        my_char = self.key_labels[my_row][my_column]
                        if my_char == self.ret_char:
                            return key_strokes
                        no_press = False
                    if button_value == 1 and no_press_old == True and no_press == False:
                        key_strokes = key_strokes + my_char
            no_press_old = no_press
            sleep(0.25)
