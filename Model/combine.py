from PIL import Image

class TheImages:
    def __init__(self, file_name, img1_path, img2_path = 'Data/Source/DialoxLogo.png'):
        self.file_name = file_name
        self.img1_path = r"{}".format(img1_path)
        self.img2_path = r"{}".format(img2_path)
    def create(self):
        img1 = Image.open(self.img1_path)
        img2 = Image.open(self.img2_path)
        img1.paste(img2, (0, 0), mask=img2)
        result_path = f"Data/Result/{self.file_name[:-5]}.png"
        img1.save(f"{result_path}", "PNG")
        return result_path