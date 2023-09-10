import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import urllib.request


# 受け取ったjsonから、話者・スタイル・idに分けた辞書を作る
def speakers():
    mapping = {'四国めたん': {'あまあま': 0, 'ノーマル': 2, 'セクシー': 4, 'ツンツン': 6}}
    try:
        request = requests.get('https://static.tts.quest/voicevox_speakers.json').json()
        if 'success' not in request:
            for idx, option in enumerate(request):
                # 'VOICEVOX:' の部分を削除
                option = option[9:]
                # '（' と '）' の間のスピーカー名を抽出
                speaker = option.split('（')[0]
                # '（' と '）' の間のスタイル名を抽出
                style = option.split('（')[1][:-1]
    
                # 話者の追加
                if speaker not in mapping:
                    mapping[speaker] = {}
                # スタイル情報とidを追加
                mapping[speaker][style] = idx

        return mapping  # 辞書形式で返す
    except requests.exceptions.RequestException as e:
        print(f'Error fetching speakers: {e}')
        return mapping


speakers = speakers()


# スピーカーが選択されたときにスタイルのプルダウンリストをアクティブにする関数
def enable_style_selection(event):
    # 選択したスピーカーに関連するスタイルのリストを取得
    speaker_data = speakers[speaker_combo.get()]
    style_values = list(speaker_data.keys())
    # スタイルの選択肢を更新
    style_combo['values'] = style_values
    style_combo['state'] = 'readonly'  # スタイルを選択可能にするかどうかを設定
    style_combo.set(style_values[0])  # デフォルトで最初のスタイルを選択
    style_combo.speaker_data = speaker_data  # スタイルデータをコンボボックスのインスタンス変数として保存


def send_api_request():
    speaker_data = style_combo.speaker_data  # コンボボックスからスタイルデータを取得
    # 話者とスタイルから、idを取得
    speaker_id = speaker_data[style_combo.get()]
    print(f'話者:{speaker_combo.get()}　スタイル:{style_combo.get()}　id:{speaker_id}')
    speakerSelect.config(text=f'話者:{speaker_combo.get()}　スタイル:{style_combo.get()}　id:{speaker_id}')

    try:
        # APIリクエストのパラメータを作成
        params = {
            'key': 'Z4F4i255201_58n',
            'speaker': speaker_id,
            'text': text.get()
        }

        # APIにリクエストを送信
        response = requests.get('https://api.tts.quest/v3/voicevox/synthesis', params=params)
        response_data = response.json()

        # 音声ファイルをダウンロード
        if 'retryAfter' in response_data:
            retry_after = response_data['retryAfter']
            print(f'time:{1 + retry_after}')
            win.after(1000 * (1 + retry_after), send_api_request)
        elif 'mp3StreamingUrl' in response_data:
            mode = '高速' if response_data['isApiKeyValid'] else '低速'
            print(mode)
            labelMode.config(text=f'{mode}')
            mp3_url = response_data['mp3StreamingUrl']
            urllib.request.urlretrieve(mp3_url, 'sample.mp3')
            messagebox.showinfo('ダイアログタイトル', 'ダウンロードが完了しました。')
        elif 'errorMessage' in response_data:
            messagebox.showerror('エラー', response_data['errorMessage'])
        else:
            messagebox.showerror('エラー', '音声の取得に失敗しました。')

    except Exception as e:
        messagebox.showerror('エラー', str(e))


# ウィンドウを作成
win = tk.Tk()
win.title('VOICEVOX')
win.geometry('400x300')

# モード
labelMode = tk.Label(win, text='')
labelMode.pack()

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
speaker_label = ttk.Label(win, text='Speaker:')
speaker_label.pack()
speaker_combo = ttk.Combobox(win, values=list(speakers.keys()))
speaker_combo.pack()
# Speaker選択時にStyleの選択肢を更新
speaker_combo.bind('<<ComboboxSelected>>', enable_style_selection)

# プルダウンリスト (Style)
style_label = ttk.Label(win, text='Style:')
style_label.pack()
style_combo = ttk.Combobox(win, values=[])
style_combo.pack()
style_combo['state'] = 'disabled'  # 初期状態ではスタイルは選択不可

# VoiceVoxの話者データを表示
speakerSelect = ttk.Label(win, text='')
speakerSelect.pack()

# OKボタンを作成
okButton = tk.Button(win, text='OK', command=send_api_request)
okButton.pack()

# ウィンドウを表示，イベントループへ
win.mainloop()
