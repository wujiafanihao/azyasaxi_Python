import requests
import os
import tkinter as tk
from tkinter import ttk
import asyncio
from threading import Thread

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("明哥黑市宠物下载器")

        self.url_var = tk.StringVar(value="https://appcute.im/webapi/pet/list?cat_id=")
        self.id_var = tk.StringVar()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Cat ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.id_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)

        self.download_button = ttk.Button(frame, text="Download", command=self.start_download)
        self.download_button.grid(row=0, column=2, sticky=tk.W, pady=5)

        self.pause_button = ttk.Button(frame, text="Pause", command=self.pause_download, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=3, sticky=tk.W, pady=5)

        self.progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

    def start_download(self):
        cat_id = self.id_var.get()
        if cat_id:
            self.url_var.set(f"https://appcute.im/webapi/pet/list?cat_id={cat_id}")
            self.download_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.progress["value"] = 0
            self.root.update_idletasks()
            Thread(target=self.run_download).start()

    def pause_download(self):
        pass  # Implement pause functionality if needed

    def run_download(self):
        asyncio.run(self.fetch_pet_list(self.url_var.get()))

    async def fetch_pet_list(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data["error"] == 0:
                pet_list = data["data"].get("list", [])
                if pet_list:
                    total_files = sum(len(pet.get("videos", [])) + len(pet.get("photos", [])) for pet in pet_list)
                    self.progress["maximum"] = total_files
                    for pet in pet_list:
                        name = pet.get("name", "unknown")
                        pet_id = pet.get("id", "unknown")
                        videos = pet.get("videos", [])
                        photos = pet.get("photos", [])
                        save_path = os.path.join("video", name, str(pet_id))
                        if not os.path.exists(save_path):
                            os.makedirs(save_path)
                        for video in videos:
                            video_extension = video.split(".")[-1]
                            video_name = f"{name}_{pet_id}.{video_extension}"
                            video_path = os.path.join(save_path, video_name)
                            await self.download_file(video, video_path)
                            self.progress["value"] += 1
                            self.root.update_idletasks()
                        for photo in photos:
                            photo = photo.split("!b")[0]  # Remove the '!b' suffix
                            photo_extension = photo.split(".")[-1]
                            photo_name = f"{name}_{pet_id}_photo.{photo_extension}"
                            photo_path = os.path.join(save_path, photo_name)
                            await self.download_file(photo, photo_path)
                            self.progress["value"] += 1
                            self.root.update_idletasks()
                else:
                    print("No pets found in the list.")
            else:
                print(f"Error: {data['msg']}")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
        self.download_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    async def download_file(self, url, path):
        response = requests.get(url, stream=True, headers=self.headers)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print(f"Downloaded: {path}")
        else:
            print(f"Failed to download file from {url}. Status code: {response.status_code}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()