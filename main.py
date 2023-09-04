import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import urllib.request

apiKey = False
mode = ''


def send_api_request():
    global apiKey
    global mode

    selected_speaker = speaker_combo.get()
    selected_style = style_combo.get()
    speaker_id = 0

    # 話者とスタイルから、idを取得
    for entry in data:
        if entry["name"] == selected_speaker:
            for style in entry["styles"]:
                if style["name"] == selected_style:
                    speaker_id = style['id']
                    result_label.config(text=f"id: {style['id']}")

    try:
        # APIエンドポイントとパラメータを構築
        api_endpoint = 'https://api.tts.quest/v3/voicevox/synthesis'
        text_to_speak = text.get()

        # APIリクエストのパラメータを作成
        params = {
            'key': 'Z4F4i255201_58n',
            'speaker': speaker_id,
            'text': text_to_speak
        }

        # APIにリクエストを送信
        response = requests.get(api_endpoint, params=params)
        response_data = response.json()

        # 音声ファイルをダウンロード
        if 'mp3StreamingUrl' in response_data:
            mode = '高速' if response_data['isApiKeyValid'] else '低速'
            mp3_url = response_data['mp3StreamingUrl']
            urllib.request.urlretrieve(mp3_url, "sample.mp3")
            messagebox.showinfo('ダイアログタイトル', 'ダウンロードが完了しました。')
        elif 'errorMessage' in response_data:
            messagebox.showerror('エラー', response_data['errorMessage'])
        else:
            messagebox.showerror('エラー', '音声の取得に失敗しました。')

    except Exception as e:
        messagebox.showerror('エラー', str(e))


# 受け取ったjsonから、話者・スタイル・idに分けたJSONデータを作る
def speak_json():
    mapping = {}

    for idx, option in enumerate(requests.get('https://static.tts.quest/voicevox_speakers.json').json()):
        # "VOICEVOX:" の部分を削除
        option = option[9:]

        # "（" と "）" の間のスピーカー名を抽出
        speaker = option.split("（")[0]

        # "（" と "）" の間のスタイル名を抽出
        style = option.split("（")[1][:-1]

        if speaker not in mapping:
            mapping[speaker] = {"name": speaker, "styles": []}

        # スタイル情報を追加
        mapping[speaker]["styles"].append({"name": style, "id": idx})

    # マッピングをリストに変換
    result = list(mapping.values())

    # JSON形式に変換
    return json.dumps(result, indent=4, ensure_ascii=False)


# JSONデータを読み込む
data = json.loads(speak_json())


# スピーカーが選択されたときにスタイルのプルダウンリストをアクティブにする関数
def enable_style_selection(event):
    selected_speaker = speaker_combo.get()
    for entry in data:
        if entry["name"] == selected_speaker:
            style_values = [style["name"] for style in entry["styles"]]
            style_combo["values"] = style_values
            style_combo["state"] = "readonly"  # スタイルを選択可能にする
            style_combo.set(style_values[0])  # デフォルトで最初のスタイルを選択


# ウィンドウを作成
win = tk.Tk()
win.title("VOICEVOX")
win.geometry("400x300")

# モード
labelHeights = tk.Label(win, text=mode)
labelHeights.pack()

# 名前ラベル
label = tk.Label(win, text='文字を入力してください')
label.pack()
# 名前のテキストボックス
text = tk.Entry(win)
text.pack()

# 声質ラベル
labelHeight = tk.Label(win, text='話者を選択してください')
labelHeight.pack()

# プルダウンリスト (Speaker)
speaker_label = ttk.Label(win, text="Speaker:")
speaker_label.pack()
speaker_values = [entry["name"] for entry in data]
speaker_combo = ttk.Combobox(win, values=speaker_values)
speaker_combo.pack()
# プルダウンリスト (Style)
style_label = ttk.Label(win, text="Style:")
style_label.pack()
style_combo = ttk.Combobox(win, values=[])
style_combo.pack()
style_combo["state"] = "disabled"  # 初期状態ではスタイルは選択不可
# ID表示用ラベル
result_label = ttk.Label(win, text="")
result_label.pack()
# Speaker選択時にStyleの選択肢を更新
speaker_combo.bind("<<ComboboxSelected>>", enable_style_selection)
# VoiceVoxの話者データを取得
speakerSelect = ttk.Label(win, text="")

# OKボタンを作成
okButton = tk.Button(win, text='OK', command=send_api_request)
okButton.pack()

# ウィンドウを表示，イベントループへ
win.mainloop()
