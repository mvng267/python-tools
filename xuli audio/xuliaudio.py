import os
import subprocess

def convert_audio_with_ffmpeg(input_folder, output_folder):
    # Tạo thư mục đầu ra nếu chưa tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Duyệt qua các file trong thư mục đầu vào
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        
        # Tạo đường dẫn file đầu ra với đuôi .mp3
        output_file = os.path.splitext(filename)[0] + ".mp3"
        output_path = os.path.join(output_folder, output_file)

        print(f"Đang xử lý file: {input_path}")

        # Lệnh ffmpeg để chuyển đổi
        command = [
            "ffmpeg", "-i", input_path,  # Đường dẫn file đầu vào
            "-ar", "16000",             # Sample rate 16 kHz
            "-ac", "1",                 # Mono
            output_path                 # Đường dẫn file đầu ra
        ]

        try:
            # Chạy lệnh ffmpeg
            subprocess.run(command, check=True)
            print(f"Chuyển đổi thành công: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi xử lý file {input_path}: {e}")
        except FileNotFoundError:
            print("Lỗi: Không tìm thấy ffmpeg. Hãy cài đặt và thêm vào PATH.")
        except Exception as e:
            print(f"Lỗi không xác định với file {input_path}: {e}")

# Đường dẫn thư mục đầu vào và đầu ra
input_folder = "MP3"
output_folder = "output"

if os.path.exists(input_folder):
    convert_audio_with_ffmpeg(input_folder, output_folder)
else:
    print(f"Thư mục '{input_folder}' không tồn tại!")
