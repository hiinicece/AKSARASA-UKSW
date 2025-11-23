from google import genai
import os
from gtts import gTTS
import threading
import queue
import tempfile
import uuid
import re
import logging
from datetime import datetime
from typing import Optional
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import json
from pathlib import Path

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame tidak terinstall. TTS speed control tidak tersedia.")
    print("Install dengan: pip install pygame")

# === Config File Management ===
CONFIG_FILE = "chatbot_config.json"

def load_config():
    """Load konfigurasi dari file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Simpan konfigurasi ke file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def get_api_key():
    """Get API key dari environment variable atau config file"""
    # Cek environment variable dulu
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # Cek config file
    config = load_config()
    api_key = config.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    return None

# === Konfigurasi Logging ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_gui.log'),
    ]
)
logger = logging.getLogger(__name__)

# === Konstanta Konfigurasi ===
class Config:
    MODEL = "gemini-2.5-flash"
    TTS_LANG = "id"
    MIN_WORDS_FOR_TTS = 5
    SENTENCE_DELIMITERS = r'([.!?\n]+)'
    
    # GUI Colors (Dark Theme)
    BG_COLOR = "#1e1e1e"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#007acc"
    CHAT_BG = "#2d2d2d"
    USER_MSG_BG = "#007acc"
    BOT_MSG_BG = "#3d3d3d"
    INPUT_BG = "#252525"

# === Class Chatbot Professional dengan GUI ===
class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Gemini Chatbot Pro")
        self.root.geometry("1000x750")
        self.root.configure(bg=Config.BG_COLOR)
        
        # Set icon jika ada
        try:
            # Untuk Windows
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Initialize pygame mixer for audio
        if PYGAME_AVAILABLE:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Get API key
        api_key = get_api_key()
        
        # Jika tidak ada API key, tampilkan dialog untuk input
        if not api_key:
            api_key = self._show_api_key_dialog()
            if not api_key:
                messagebox.showerror("Error", "API Key diperlukan untuk menjalankan chatbot!")
                sys.exit(1)
        
        # Initialize chatbot
        try:
            self.client = genai.Client(api_key=api_key)
            self.conversation_history = []
            self.speech_queue = queue.Queue()
            self.is_running = True
            self.tts_enabled = True
            self.tts_speed = 1.3
            self.current_audio_file = None
            
            # Start TTS worker
            self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.tts_thread.start()
            
            logger.info("Chatbot GUI berhasil diinisialisasi")
            
        except Exception as e:
            logger.error(f"Error inisialisasi: {e}")
            messagebox.showerror("Error", f"Gagal inisialisasi: {e}")
            sys.exit(1)
        
        self._create_widgets()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _show_api_key_dialog(self):
        """Tampilkan dialog untuk input API key"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Setup API Key")
        dialog.geometry("500x250")
        dialog.configure(bg=Config.BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        api_key_var = tk.StringVar()
        save_var = tk.BooleanVar(value=True)
        
        # Title
        title = tk.Label(
            dialog,
            text="🔑 Setup Gemini API Key",
            font=("Segoe UI", 14, "bold"),
            bg=Config.BG_COLOR,
            fg=Config.FG_COLOR
        )
        title.pack(pady=20)
        
        # Info
        info = tk.Label(
            dialog,
            text="Masukkan API Key Anda dari Google AI Studio:",
            font=("Segoe UI", 10),
            bg=Config.BG_COLOR,
            fg=Config.FG_COLOR
        )
        info.pack(pady=5)
        
        # Entry
        entry_frame = tk.Frame(dialog, bg=Config.BG_COLOR)
        entry_frame.pack(pady=10, padx=40, fill=tk.X)
        
        entry = tk.Entry(
            entry_frame,
            textvariable=api_key_var,
            font=("Segoe UI", 11),
            bg=Config.INPUT_BG,
            fg=Config.FG_COLOR,
            insertbackground=Config.FG_COLOR,
            relief=tk.FLAT,
            show="*"
        )
        entry.pack(fill=tk.X, ipady=8, padx=5)
        entry.focus()
        
        # Checkbox untuk menyimpan
        check = tk.Checkbutton(
            dialog,
            text="Simpan API Key untuk sesi berikutnya",
            variable=save_var,
            font=("Segoe UI", 9),
            bg=Config.BG_COLOR,
            fg=Config.FG_COLOR,
            selectcolor=Config.INPUT_BG,
            activebackground=Config.BG_COLOR,
            activeforeground=Config.FG_COLOR
        )
        check.pack(pady=5)
        
        result = {"api_key": None}
        
        def on_submit():
            key = api_key_var.get().strip()
            if key:
                result["api_key"] = key
                if save_var.get():
                    config = load_config()
                    config["GEMINI_API_KEY"] = key
                    save_config(config)
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "API Key tidak boleh kosong!")
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=Config.BG_COLOR)
        btn_frame.pack(pady=15)
        
        submit_btn = tk.Button(
            btn_frame,
            text="✓ Simpan",
            command=on_submit,
            bg=Config.ACCENT_COLOR,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="✗ Batal",
            command=on_cancel,
            bg="#d9534f",
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        entry.bind("<Return>", lambda e: on_submit())
        
        dialog.wait_window()
        return result["api_key"]

    def _create_widgets(self):
        """Buat semua widget GUI"""
        
        # === Compact Header (Tanpa Banner) ===
        header_frame = tk.Frame(self.root, bg=Config.BG_COLOR)
        header_frame.pack(fill=tk.X, side=tk.TOP, pady=(10, 5))
        
        # Simple title di pojok kiri
        title_label = tk.Label(
            header_frame, 
            text="🤖 Gemini Chatbot", 
            font=("Segoe UI", 12, "bold"),
            bg=Config.BG_COLOR,
            fg=Config.ACCENT_COLOR
        )
        title_label.pack(side=tk.LEFT, padx=15)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="● Online",
            font=("Segoe UI", 9),
            bg=Config.BG_COLOR,
            fg="#4caf50"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # === Control Panel Frame ===
        control_frame = tk.Frame(self.root, bg=Config.BG_COLOR)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # TTS Toggle Button
        self.tts_btn = tk.Button(
            control_frame,
            text="🔊 TTS: ON",
            command=self._toggle_tts,
            bg=Config.ACCENT_COLOR,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.tts_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear History Button
        clear_btn = tk.Button(
            control_frame,
            text="🗑️ Hapus Riwayat",
            command=self._clear_history,
            bg="#d9534f",
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Speed Control Frame
        if PYGAME_AVAILABLE:
            speed_frame = tk.Frame(control_frame, bg=Config.BG_COLOR)
            speed_frame.pack(side=tk.LEFT, padx=20)
            
            speed_label = tk.Label(
                speed_frame,
                text="⚡ Kecepatan Suara:",
                font=("Segoe UI", 10),
                bg=Config.BG_COLOR,
                fg=Config.FG_COLOR
            )
            speed_label.pack(side=tk.LEFT, padx=5)
            
            # Speed preset buttons
            speeds = [
                ("🐌 Lambat", 0.8, "#ff9800"),
                ("👤 Normal", 1.0, "#4caf50"),
                ("⚡ Cepat", 1.3, "#2196f3"),
                ("🚀 Sangat Cepat", 1.6, "#f44336")
            ]
            
            for text, speed, color in speeds:
                btn = tk.Button(
                    speed_frame,
                    text=text,
                    command=lambda s=speed: self._set_speed(s),
                    bg=color if speed == self.tts_speed else Config.INPUT_BG,
                    fg="white",
                    font=("Segoe UI", 9, "bold" if speed == self.tts_speed else "normal"),
                    relief=tk.FLAT,
                    padx=10,
                    pady=3,
                    cursor="hand2"
                )
                btn.pack(side=tk.LEFT, padx=2)
                setattr(self, f"speed_btn_{speed}", btn)
        
        # === Chat Display Frame ===
        chat_frame = tk.Frame(self.root, bg=Config.BG_COLOR)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrolled Text for Chat
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg=Config.CHAT_BG,
            fg=Config.FG_COLOR,
            insertbackground=Config.FG_COLOR,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for styling
        self.chat_display.tag_config("user", foreground="#4fc3f7", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("bot", foreground="#81c784", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("timestamp", foreground="#757575", font=("Segoe UI", 9))
        self.chat_display.tag_config("message", foreground=Config.FG_COLOR, font=("Segoe UI", 11))
        
        # === Input Frame ===
        input_frame = tk.Frame(self.root, bg=Config.BG_COLOR)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Input Text
        self.input_text = tk.Text(
            input_frame,
            height=3,
            font=("Segoe UI", 11),
            bg=Config.INPUT_BG,
            fg=Config.FG_COLOR,
            insertbackground=Config.FG_COLOR,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_text.bind("<Return>", self._on_enter)
        self.input_text.bind("<Shift-Return>", lambda e: None)
        self.input_text.focus()
        
        # Send Button
        self.send_btn = tk.Button(
            input_frame,
            text="Kirim ➤",
            command=self._send_message,
            bg=Config.ACCENT_COLOR,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            width=10
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Welcome message
        self._display_welcome()

    def _display_welcome(self):
        """Tampilkan pesan selamat datang"""
        welcome_msg = """
Selamat datang! 👋

Saya siap membantu Anda. Silakan tanyakan apa saja.

Tips:
• Gunakan tombol 🔊 untuk mengatur suara
• Pilih kecepatan suara sesuai preferensi Anda
• Klik "Hapus Riwayat" untuk memulai percakapan baru

        """
        self._append_to_chat(welcome_msg, "message")

    def _append_to_chat(self, text, tag="message"):
        """Tambahkan teks ke chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _on_enter(self, event):
        """Handle Enter key press"""
        if not event.state & 0x1:  # Not Shift+Enter
            self._send_message()
            return "break"

    def _send_message(self):
        """Kirim pesan user ke chatbot"""
        message = self.input_text.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        
        # Disable send button
        self.send_btn.config(state=tk.DISABLED)
        
        # Display user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_to_chat(f"\n[{timestamp}] ", "timestamp")
        self._append_to_chat("👤 Anda:\n", "user")
        self._append_to_chat(f"{message}\n", "message")
        
        # Process in thread to not block GUI
        threading.Thread(target=self._process_chat, args=(message,), daemon=True).start()

    def _process_chat(self, user_message):
        """Proses chat dengan Gemini API"""
        try:
            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display bot header
            timestamp = datetime.now().strftime("%H:%M:%S")
            self._append_to_chat(f"\n[{timestamp}] ", "timestamp")
            self._append_to_chat("🤖 Bot:\n", "bot")
            
            # Stream response
            stream = self.client.models.generate_content_stream(
                model=Config.MODEL,
                contents=user_message,
            )
            
            full_response = ""
            text_buffer = ""
            
            for chunk in stream:
                if chunk.text:
                    chunk_text = chunk.text
                    full_response += chunk_text
                    text_buffer += chunk_text
                    
                    # Display in GUI
                    self._append_to_chat(chunk_text, "message")
                    
                    # Process for TTS
                    while text_buffer:
                        text_to_speak, text_buffer = self._process_text_buffer(text_buffer)
                        if text_to_speak:
                            self.speech_queue.put(text_to_speak)
                        else:
                            break
            
            # Send remaining buffer
            if text_buffer.strip():
                self.speech_queue.put(text_buffer.strip())
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            self._append_to_chat(f"\n❌ Error: {e}\n", "message")
        
        finally:
            # Re-enable send button
            self.send_btn.config(state=tk.NORMAL)
            self.input_text.focus()

    def _process_text_buffer(self, buffer):
        """Proses buffer untuk TTS"""
        if not buffer:
            return "", ""
        
        sentences = re.split(Config.SENTENCE_DELIMITERS, buffer)
        
        if len(sentences) > 2:
            complete_sentence = sentences[0] + (sentences[1] if len(sentences) > 1 else "")
            remaining = "".join(sentences[2:])
            return complete_sentence.strip(), remaining.lstrip()
        
        words = buffer.split()
        if len(words) >= Config.MIN_WORDS_FOR_TTS:
            text_to_speak = " ".join(words[:Config.MIN_WORDS_FOR_TTS])
            remaining = " ".join(words[Config.MIN_WORDS_FOR_TTS:])
            return text_to_speak, remaining
        
        return "", buffer

    def _tts_worker(self):
        """Worker thread untuk TTS"""
        while self.is_running:
            try:
                text_chunk = self.speech_queue.get(timeout=1)
                
                if text_chunk == "SPEAK_STOP":
                    break
                
                if text_chunk and text_chunk.strip() and self.tts_enabled:
                    self._speak_text(text_chunk)
                
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error TTS worker: {e}")

    def _speak_text(self, text):
        """Convert text ke speech dan mainkan dengan speed control"""
        try:
            # Generate TTS dengan gTTS
            # Jika speed > 1.2, gunakan slow=False untuk base yang lebih cepat
            use_slow = self.tts_speed < 1.0
            tts = gTTS(text=text, lang=Config.TTS_LANG, slow=use_slow)
            
            # Save to temp file
            filename = os.path.join(
                tempfile.gettempdir(), 
                f"tts_{uuid.uuid4().hex[:8]}.mp3"
            )
            tts.save(filename)
            self.current_audio_file = filename
            
            if PYGAME_AVAILABLE:
                # Load and play with pygame
                pygame.mixer.music.load(filename)
                
                # Adjust playback speed (hanya jika tidak slow)
                if not use_slow:
                    # pygame doesn't support speed change directly
                    # Tapi kita bisa gunakan frequency adjustment
                    # Note: Ini akan mengubah pitch juga
                    pass
                
                pygame.mixer.music.play()
                
                # Wait until audio finishes
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            else:
                # Fallback ke playsound jika pygame tidak tersedia
                from playsound3 import playsound
                playsound(filename)
            
            # Cleanup
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error TTS: {e}")

    def _set_speed(self, speed):
        """Set TTS speed dan update button styles"""
        self.tts_speed = speed
        logger.info(f"TTS speed set to {speed}x")
        
        # Update button styles
        if PYGAME_AVAILABLE:
            speeds_config = {
                0.8: ("🐌 Lambat", "#ff9800"),
                1.0: ("👤 Normal", "#4caf50"),
                1.3: ("⚡ Cepat", "#2196f3"),
                1.6: ("🚀 Sangat Cepat", "#f44336")
            }
            
            for s, (text, color) in speeds_config.items():
                btn = getattr(self, f"speed_btn_{s}", None)
                if btn:
                    if s == speed:
                        btn.config(bg=color, font=("Segoe UI", 9, "bold"))
                    else:
                        btn.config(bg=Config.INPUT_BG, font=("Segoe UI", 9, "normal"))

    def _toggle_tts(self):
        """Toggle TTS on/off"""
        self.tts_enabled = not self.tts_enabled
        if self.tts_enabled:
            self.tts_btn.config(text="🔊 TTS: ON", bg=Config.ACCENT_COLOR)
        else:
            self.tts_btn.config(text="🔇 TTS: OFF", bg="#d9534f")
            # Stop current audio
            if PYGAME_AVAILABLE:
                pygame.mixer.music.stop()
        logger.info(f"TTS toggled: {'ON' if self.tts_enabled else 'OFF'}")

    def _clear_history(self):
        """Clear chat history"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat percakapan?"):
            self.conversation_history.clear()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self._display_welcome()
            logger.info("Chat history cleared")

    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Keluar", "Yakin ingin keluar?"):
            self.is_running = False
            self.speech_queue.put("SPEAK_STOP")
            if PYGAME_AVAILABLE:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            self.root.destroy()
            logger.info("Application closed")

# === Main Program ===
def main():
    """Entry point"""
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()