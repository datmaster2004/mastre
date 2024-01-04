import tkinter as tk
from tkinter import messagebox, font
import socket
import threading
import mss
import pickle
import time
import io
import zlib  # Thư viện nén dữ liệu

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server")

        # Thiết lập phông chữ
        large_font = font.Font(size=12)

        # Các widget
        tk.Label(root, text="Host:", font=large_font).grid(row=0, column=0)
        self.host_entry = tk.Entry(root, font=large_font)
        self.host_entry.grid(row=0, column=1)
        self.host_entry.insert(0, '192.168.137.1')

        tk.Label(root, text="Port:", font=large_font).grid(row=1, column=0)
        self.port_entry = tk.Entry(root, font=large_font)
        self.port_entry.grid(row=1, column=1)
        self.port_entry.insert(0, '8888')

        self.start_button = tk.Button(root, text="Start Server", command=self.start_server, font=large_font)
        self.start_button.grid(row=2, column=0)

        self.stop_button = tk.Button(root, text="Stop Server", command=self.stop_server, state=tk.DISABLED, font=large_font)
        self.stop_button.grid(row=2, column=1)

        self.server = None
        self.running = False


    def start_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((host, port))
            self.server.listen()
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            threading.Thread(target=self.accept_connections, daemon=True).start()
            messagebox.showinfo("Server", "Server is running.")
        except Exception as e:
            messagebox.showerror("Server Error", str(e))
            if self.server:
                self.server.close()
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def accept_connections(self):
        while self.running:
            try:
                client_socket, address = self.server.accept()
                print(f"Connected by {address}")

                # Gửi hình ảnh màn hình liên tục cho client
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connections: {e}")
                break  # Thoát khi có lỗi
    def handle_client(self, client_socket):
        try:
            while self.running and client_socket:
                try:
                    self.send_screenshot(client_socket)
                    time.sleep(0.1)  # Độ trễ 0.1 giây
                except ConnectionError as ce:
                    print(f"Connection error with client {client_socket}: {ce}")
                    break  # Thoát khỏi vòng lặp khi kết nối mất
                except Exception as e:
                    print(f"Error sending screenshot to client {client_socket}: {e}")
                    break  # Thoát khỏi vòng lặp khi có lỗi khác
        except Exception as e:
            print(f"General error with client {client_socket}: {e}")
        # finally:
        #     client_socket.close()  # Đóng kết nối socket một cách an toàn


    def stop_server(self):
        self.running = False
        self.server.close()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Server", "Server has stopped.")

    def capture_screen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Chọn màn hình chính
            sct_img = sct.grab(monitor)
            return sct_img

    def send_screenshot(self, client_socket):
        sct_img = self.capture_screen()

        # Chuyển đổi sang định dạng PNG và nén
        with io.BytesIO() as buffer:
            sct_img.image.save(buffer, format="PNG")
            compressed_img_data = zlib.compress(buffer.getvalue())

        # Gửi kích thước của dữ liệu nhị phân nén
        client_socket.sendall(len(compressed_img_data).to_bytes(4, 'big'))

        # Gửi dữ liệu hình ảnh nén
        client_socket.sendall(compressed_img_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()