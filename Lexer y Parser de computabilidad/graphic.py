# Import libraries
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from PIL import Image, ImageTk

# Generates a bar chart and returns it as an image for Tkinter
def create_chart(count):

    plt.figure(figsize=(6, 6))
    sns.barplot(x = list(count.values()), y = list(count.keys()), orient = 'h')
    plt.xlabel("Count")
    plt.ylabel("Categories")
    plt.title("Category Frequency in the File")
    plt.tight_layout()

    # Save image to memory
    buffer = BytesIO()
    plt.savefig(buffer, format = 'png')
    buffer.seek(0)
    plt.close()

    # Convert image for Tkinter
    img = Image.open(buffer)
    img = ImageTk.PhotoImage(img)

    return img