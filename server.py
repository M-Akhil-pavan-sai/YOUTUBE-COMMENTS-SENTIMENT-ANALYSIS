from flask import Flask, request, request, render_template
from predict import predict_sentiments
from youtube import get_video_comments
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def get_video(video_id):
    if not video_id:
        return {"error": "video_id is required"}

    comments = get_video_comments(video_id)
    predictions = predict_sentiments(comments)

    positive = predictions.count("Positive")
    negative = predictions.count("Negative")

    summary = {
        "positive": positive,
        "negative": negative,
        "num_comments": len(comments),
        "rating": (positive / len(comments)) * 100
    }

    return {"predictions": predictions, "comments": comments, "summary": summary}


@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    comments = []
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_id = video_url.split("v=")[1]
        data = get_video(video_id)

        summary = data['summary']
        comments = list(zip(data['comments'], data['predictions']))
    return render_template('index.html', summary=summary, comments=comments)

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass the error to the template
    # e.name is the status code name, e.code is the status code, e.description gives detail about the error
    error_info = {
        'error_title': getattr(e, 'name', 'Error Occurred'),
        'error_message': getattr(e, 'description', 'An unexpected error occurred.'),
        'error_code': getattr(e, 'code', 500),
    }
    return render_template('error.html', **error_info), getattr(e, 'code', 500)

if __name__ == '__main__':
    app.run(debug=True)