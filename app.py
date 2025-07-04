from flask import Flask, render_template, request
import joblib
import numpy as np
import re

app = Flask(__name__)
model = joblib.load("classBalanced.pkl")  # 재현율 강화된 모델

# 1️⃣ 비밀번호에서 특성 추출
def extract_features(password):
    length = len(password)
    capital = sum(1 for c in password if c.isupper())
    small = sum(1 for c in password if c.islower())
    digit = sum(1 for c in password if c.isdigit())
    special = len(re.findall(r'[^A-Za-z0-9]', password))

    return {
        'length': length,
        'capital': capital,
        'small': small,
        'digit': digit,
        'special': special
    }

# 2️⃣ 추출된 특성으로 점수 계산
def calculate_score(row):
    score = 0

    # 길이 점수
    if row['length'] < 5:
        score += 0
    elif 5 <= row['length'] <= 8:
        score += 1
    elif 9 <= row['length'] <= 12:
        score += 2
    else:  # 12자 이상
        score += 3

    # 대문자 점수
    if row['capital'] == 0:
        score += 0
    elif 1 <= row['capital'] <= 3:
        score += 1
    else:
        score += 2

    # 소문자 점수
    if row['small'] <= 1:
        score += 0
    elif 2 <= row['small'] <= 3:
        score += 0.8
    elif 4 <= row['small'] <= 5:
        score += 1.6
    else:
        score += 2.4

    # 숫자 점수
    if row['digit'] <= 1:
        score += 0
    elif 2 <= row['digit'] <= 3:
        score += 0.38
    else:
        score += 0.76

    # 특수문자 점수
    if row['special'] == 0:
        score += 0
    elif 1 <= row['special'] <= 2:
        score += 1.23
    else:
        score += 2.46

    return score

# 3️⃣ 점수에 따라 강도 등급 지정
def classify_strength(score): 
    if score <= 1:
        return 1  # 매우 취약
    elif score <= 3:
        return 2  # 취약
    elif score <= 5:
        return 3  # 보통
    elif score <= 7:
        return 4  # 안전
    else:
        return 5  # 매우 안전

# 4️⃣ 부족한 요소 피드백 제공
def get_detailed_feedback(features):
    messages = []

    if features['length'] < 9:
        messages.append("🔹 비밀번호 길이가 조금 아쉽다, 9자 이상으로 늘려봐!")
    
    if features['capital'] == 0:
        messages.append("🔹 대문자가 없어! 최소 1개 이상 포함해봐!")
    
    if features['small'] <= 3:
        messages.append("🔹 소문자가 부족해, 4자 이상이면 더 안전해질 거야!")
    
    if features['digit'] <= 1:
        messages.append("🔹 숫자가 부족해! 최소 2자 이상은 포함해보는 거 어때?")
    
    if features['special'] == 0:
        messages.append("🔹 특수문자가 없네? @, !, # 같은 문자들을 포함해보자!")

    if not messages:
        messages.append("✅ 주요 조건을 모두 만족하고 있어! 아주 잘하고 있구만!")

    return messages

# 5️⃣ 라우트 구성
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pw = request.form["password"]
        features = extract_features(pw)
        score = calculate_score(features)
        strength = classify_strength(score)
        detailed_feedback = get_detailed_feedback(features)

        feedback = {
            1: "🔴 매우 취약: 이런 비밀번호는 그냥 안돼! 바로 털릴 거라구!!",
            2: "🟠 취약: 길이나 문자 조합이 부족한가봐, 아래 보완할 점 참고해서 수정해봐!",
            3: "🟡 보통: 조금만 더 신경쓰면 더 확실히 안전한 비밀번호가 될 수 있을 것 같아!",
            4: "🟢 안전: 이 정도면 나름 괜찮은 비밀번호 같은데?",
            5: "🔵 매우 안전: 완벽한 비밀번호야! 앞으로도 이렇게 만드는 습관을 기르도록!"
        }.get(strength, "❓ 알 수 없는 결과입니다.")

        return render_template(
            "result.html",
            password=pw,
            score=strength,
            feedback=feedback,
            details=detailed_feedback  # 상세 피드백 전달!
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
