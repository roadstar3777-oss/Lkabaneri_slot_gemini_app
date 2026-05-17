import streamlit as st
import google.generativeai as genai

# --- ページの設定（スマホで見やすいようにレスポンシブに設定） ---
st.set_page_config(page_title="設定判別AI", page_icon="🎰", layout="centered")

st.title("Lカバネリ海門 設定判別 AI_gemini")
st.caption("数値を入力すると、Gemini AIが設定を推測・解説します。")

# --- APIキーの設定 ---
# 安全のため、後ほどStreamlitの管理画面から登録しますが、テスト用にここに直接書くことも可能です。
# 開発時は以下のコメントアウトを外して自分のキーを入れてもOKです。
# genai.configure(api_key="あなたのGemini_APIキー")

# --- 1. 入力インターフェース（スマホで操作しやすいパーツを使用） ---
st.header("1. 実戦データの入力")

# 総回転数
total_games = st.number_input("総回転数 (G)", min_value=0, max_value=10000, value=1000, step=100)

# 下段ベル
bell_count = st.number_input("下段ベル回数 (回)", min_value=0, max_value=1000, value=10, step=1)
if bell_count > 0:
    st.text(f"👉 現在のベル確率: 1/{total_games / bell_count:.1f}")

st.divider() # 区切り線

# アイテムくじ
kuji_result = st.selectbox(
    "アイテムくじの最高示唆",
    ["なし（不明）", "小吉（設定2以上確定）", "中吉（設定4以上確定）", "大吉（設定6確定）"]
)

# トロフィー
trophy_result = st.selectbox(
    "出現した最高トロフィー",
    ["なし", "銅（設定2以上確定）", "銀（設定3以上確定）", "金（設定4以上確定）", "キリン柄（設定5以上確定）", "虹（設定6確定）"]
)

st.divider() # 区切り線

# ST中キャラクター
st.subheader("ST中のキャラクター出現回数")
col1, col2, col3 = st.columns(3)
with col1:
    female_count = st.number_input("女性", min_value=0, value=0, step=1)
with col2:
    male_count = st.number_input("男性", min_value=0, value=0, step=1)
with col3:
    mima_count = st.number_input("美馬", min_value=0, value=0, step=1)

st.divider()

# --- 2. 判別ボタンとAI処理 ---
if st.button("🤖 AI設定判別を実行する", type="primary", use_container_width=True):
    
    # ユーザーがAPIキーをシークレット（後述）に設定しているか確認
    try:
        # StreamlitのSecrets機能からAPIキーを読み込む（公開時の安全対策）
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except:
        st.error("APIキーが設定されていません。コード内、またはStreamlitのSecretsにキーを設定してください。")
        st.stop()

    with st.spinner("AIが確率を計算し、考察を生成中..."):
        # AIへのルール（System Instruction）
        system_prompt = """
        あなたはパチスロの設定判別を行うプロのAIアナリストです。
        ユーザーから提供された実戦データと、以下の「解析値（ルール）」を照らし合わせ、統計的な観点と確定要素から「各設定の期待度（%）」と「設定4以上の可能性（%）」を算出し、自然言語で分かりやすく解説してください。

        【解析値（ルール）】
        ■ 下段ベル確率: 設定1=1/121.1, 設定2=1/114.4, 設定3=1/112.8, 設定4=1/106.2, 設定5=1/104.2, 設定6=1/99.1
        ■ アイテムくじの示唆: 小吉＝設定2以上確定, 中吉＝設定4以上確定, 大吉＝設定6確定
        ■ トロフィーの示唆: 銅＝設定2以上確定, 銀＝設定3以上確定, 金＝設定4以上確定, キリン柄＝設定5以上確定, 虹＝設定6確定
        ■ ST中のキャラクター振り分け:
        設定1＝女性 50.0%：男性 50.0%：美馬 0％
        設定2＝女性 57.5%：男性 42.5%：美馬 0％ 
        設定3＝女性 41.5%：男性 58.5%：美馬 0％ 
        設定4＝女性 58.5%：男性 41.4%：美馬 0.1%
        設定5＝女性 39.9%：男性 60.0%：美馬 0.1%
        設定6＝女性 60.0%：男性 39.85%：美馬 0.15%

        【出力フォーマット】
        必ず以下の形式で回答を出力してください。結果の数値以外に無駄な前置きはしないでください。
        ### 【設定判別結果】
        ・設定1の期待度：〇%
        ・設定2の期待度：〇%
        ・設定3の期待度：〇%
        ・設定4の期待度：〇%
        ・設定5の期待度：〇%
        ・設定6の期待度：〇%

        **「このデータに基づくと、設定4以上の可能性は【 〇% 】です。」**

        ### 【考察と解説】
        （理由を分かりやすく解説）
        """

        model = genai.GenerativeModel(model_name='gemini-3-flash', system_instruction=system_prompt)

        # 画面の入力値をプロンプトにまとめる
        user_prompt = f"""
        以下のデータで判別してください。
        ・総回転数：{total_games}G
        ・下段ベル回数：{bell_count}回
        ・アイテムくじの最高示唆：{kuji_result}
        ・トロフィーの最高示唆：{trophy_result}
        ・ST中キャラ：女性{female_count}回、男性{male_count}回、美馬{mima_count}回
        """

        # AIに送信
        response = model.generate_content(user_prompt)
        
        # 結果を表示
        st.success("判別が完了しました！")
        st.markdown(response.text)