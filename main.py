import os
import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from datetime import datetime

# Create a folder to save the attendance data if it doesn't exist
folder_name = "attendance_data"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Initialize the cv2 QRCode detector
detector = cv2.QRCodeDetector()


class QRScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Add a button to start scanning
        self.scan_button = Button(text="Scan QR")
        self.scan_button.bind(on_press=self.scan_qr_code)
        self.layout.add_widget(self.scan_button)

        self.img = Image()
        self.layout.add_widget(self.img)

        # Initialize the camera
        self.cap = cv2.VideoCapture(0)

        return self.layout

    def scan_qr_code(self, instance):
        # Read frame from the camera
        ret, frame = self.cap.read()

        # Detect and decode QR code
        data, _, _ = detector.detectAndDecode(frame)

        # Check if there is a QR code in the image
        if data:
            # Get the current time
            current_time = datetime.now().time()

            # Check if the current time is within the allowed time range for CPEN 21 (7am to 9am)
            if current_time >= datetime.strptime("07:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime(
                    "09:00:00", "%H:%M:%S").time():
                status = "Present"
            else:
                status = "Late"

            # Extract user data from the QR code
            user_data = data.split('\n')  # Assuming data is newline separated
            name = user_data[0]
            id_number = user_data[1]

            # Generate filename based on date
            filename = os.path.join(folder_name, f"attendance_{datetime.now().date()}.txt")

            # Write attendance data to file
            with open(filename, "a") as f:
                f.write(
                    f"Subject: CPEN 21, Status: {status}, Time: {datetime.now().strftime('%H:%M:%S')}, Name: {name}, ID: {id_number}\n")

            print(f"Attendance marked for {name} (ID: {id_number}) - {status}")

        # Display the scanned image
        frame = cv2.flip(frame, 0)  # Flip vertically (Kivy uses inverted coordinate system)
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = texture

    def on_stop(self):
        # Release the camera when the app is stopped
        self.cap.release()


if __name__ == '__main__':
    QRScannerApp().run()


