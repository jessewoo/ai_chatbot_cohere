import cohere
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import secrets

import os
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Set a secret key for CSRF protection

cohere_api_key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(cohere_api_key)

class Form(FlaskForm):
    text = StringField('Enter text to search', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('stream.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = Form()

    cohere_api_key = os.getenv("COHERE_API_KEY")
    co = cohere.ClientV2(cohere_api_key)

    if form.validate_on_submit():
        text = form.text.data
        response = co.chat(
            model='command-a-03-2025',
            messages=[
                {
                    "role": "assistant", 
                    "content": text
                    }
            ]
        )

        output = response.message.content[0].text;
        return render_template('search.html', form=form, output=output)

    return render_template('search.html', form=form, output=None)


@app.route('/stream', methods=['GET', 'POST'])
def stream():
        def generate():
            chat_stream = co.chat_stream(
                model="command-a-03-2025",
                messages=[
                     {
                        "role": "user", 
                        "content": "What is an LLM?"
                    }
                ],
            )
            for event in chat_stream:
                if event.type == "content-delta":
                    yield f'data: {event.delta.message.content.text}\n\n'

        return Response(generate(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(debug=True)