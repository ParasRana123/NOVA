import tkinter as tk
from tkinter import filedialog, Label, Button, Text, Scrollbar, VERTICAL, END, DISABLED, NORMAL
from PIL import Image, ImageTk
import google.generativeai as genai
import os

# Load environment variables
genai.configure(api_key=("AIzaSyC_vdf5ZoD7te2A-R2tpmL0GrZgGopODfQ"))
# Configure the Generative AI API

# Initialize the main application window
root = tk.Tk()
root.title("Image Analyzer App")
root.geometry("800x600")

# Function to upload and display the image
def upload_and_display_image():
    # Open a file dialog to select an image file
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
    )
    if file_path:
        # Open and display the image
        img = Image.open(file_path)
        img.thumbnail((400, 400))  # Resize for display purposes
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.image = img_tk
        img_label.file_path = file_path  # Store file path for analysis

# Function to analyze the uploaded image
def analyze_image():
    try:
        # Ensure an image has been uploaded
        file_path = img_label.file_path
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()

        # Prepare the image data for the API
        image_parts = [
            {
                "mime_type": "image/jpeg",  # Adjust based on your image type
                "data": image_data
            }
        ]

        # Define the input prompt
        input_prompt = """
        You are an Image Analyzer with expertise in identifying and understanding the contents of any given image. Users can upload any type of image, and your role is to provide a detailed analysis of what is present in the image along with meaningful insights.

        For each image, provide:
        1. A description of the key objects, people, or elements in the image.
        2. Insights or potential applications related to the image (e.g., identifying objects for e-commerce, detecting scenarios for industrial use, or analyzing visuals for creative projects).
        3. Suggestions for enhancing or utilizing the image further (e.g., improvements for clarity, creative edits, or technological applications).

        Please ensure the insights are clear, actionable, and tailored to the context of the uploaded image.
        """

        # Initialize the Generative Model
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Generate the response
        response = model.generate_content([input_prompt, image_parts[0]])

        # Display the response
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, response.text)
        response_text.config(state=DISABLED)

    except AttributeError:
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, "Please upload an image first.")
        response_text.config(state=DISABLED)
    except Exception as e:
        response_text.config(state=NORMAL)
        response_text.delete(1.0, END)
        response_text.insert(END, f"An error occurred: {e}")
        response_text.config(state=DISABLED)

# Label to display the uploaded image
img_label = Label(root)
img_label.pack(pady=10)

# Button to upload an image
upload_button = Button(root, text="Upload Image", command=upload_and_display_image)
upload_button.pack(pady=5)

# Button to analyze the uploaded image
analyze_button = Button(root, text="Analyze Image", command=analyze_image)
analyze_button.pack(pady=5)

# Text widget to display the analysis response with a scrollbar
response_frame = tk.Frame(root)
response_frame.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(response_frame, orient=VERTICAL)
response_text = Text(response_frame, wrap=tk.WORD, width=80, height=15, state=DISABLED, yscrollcommand=scrollbar.set)
scrollbar.config(command=response_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
