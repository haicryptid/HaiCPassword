from flask import Flask, render_template, request
import joblib
import numpy as np
import re

app = Flask(__name__)
model = joblib.load("password_model.pkl")  

def extract_features(password):
    # 여기에 전처리/특성 추출 로직 넣기
    features = [
        len(password),
        int(any(c.isupper() for c in password)),
        int(any(c.islower() for c in password)),
        int(any(c.isdigit() for c in password)),
        int(bool(re.search(r'[^A-Za-z0-9]', password)))
    ]
    return np.array(features).reshape(1, -1)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pw = request.form["password"]
        features = extract_features(pw)
        prediction = model.predict(features)[0]

        # 점수에 따른 피드백
        feedback = {
            0: "취약: 대소문자, 숫자, 특수문자를 더 포함한다면 보완될 수 있을 것 같아!",
            1: "보통: 괜찮지만 더 강력하게 만들면 좋을 것 같은데?",
            2: "안전: 이 정도면 안전한 비밀번호 같아!",
        }.get(prediction, "비정상적인 입력입니다.")

        return render_template("result.html", password=pw, score=prediction, feedback=feedback)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
