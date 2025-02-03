from text_capture import TextCapture
from translate import Translator
import time


def fanyi(text):
    translator = Translator(from_lang='en', to_lang='zh')
    return translator.translate(text)

def example_callback(text: str):
    """示例回调函数"""
    print(f"捕获到文本: {text}")
    print("翻译中")
    print(f"翻译结果:{fanyi(text)}")


if __name__ == "__main__":
    # 使用示例
    capture = TextCapture(example_callback)
    capture.start_capture()
    print("文本捕获已启动...")
    print("按Win+Shift+S进行屏幕文字识别")
    print("复制文本会自动捕获")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        capture.stop_capture()
        print("文本捕获已停止")