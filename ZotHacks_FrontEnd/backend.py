import requests
import html
import random
from flask import Flask, jsonify, session, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes
app.secret_key = '7a886de2ce878452ca0104ed3df6c0fd3b7f530e0aaa25dbb45437cfcec580e8'

@app.route('/api/trivia', methods=['GET'])
def getting_trivia():
    try:
        # Get difficulty from query params, default to 'easy'
        form_diff = request.args.get('difficulty', 'easy').lower()
        
        # Validate difficulty
        if form_diff not in ['easy', 'medium', 'hard']:
            return jsonify({"error": "Invalid difficulty level. Choose from 'easy', 'medium', or 'hard'."}), 400

        # Get number of questions, default to 10, and validate it
        num_questions = request.args.get('number', 10)
        
        # Ensure number is an integer and within allowed range
        try:
            num_questions = int(num_questions)
            if num_questions < 1 or num_questions > 30:
                return jsonify({"error": "Number of questions must be between 1 and 30"}), 400
        except ValueError:
            return jsonify({"error": "Invalid number of questions. It must be an integer between 1 and 30"}), 400

        # Construct the API link for fetching trivia questions
        apilink = f'https://opentdb.com/api.php?amount={num_questions}&category=12&difficulty={form_diff}&type=multiple'

        # Make the request to the trivia API
        our_r = requests.get(apilink)
        our_r.raise_for_status()  # This will raise an error if the request failed

        # Parse JSON response from trivia API
        trivia_data = our_r.json()

        # Check if the trivia API returned a valid response with questions
        if trivia_data.get("response_code") != 0:
            return jsonify({"error": "No trivia questions available for the selected options"}), 500

        # Process and format questions
        questions = {'results': []}
        session['correct_answers'] = []

        for the_question in trivia_data['results']:
            correct_answer = html.unescape(the_question['correct_answer'])
            all_answers = [html.unescape(answer) for answer in the_question['incorrect_answers']]
            index = random.randint(0, len(all_answers))
            all_answers.insert(index, correct_answer)

            questions['results'].append({
                'question': html.unescape(the_question['question']),
                'all_answers': all_answers
            })
            session['correct_answers'].append(correct_answer)

        # Return formatted questions as JSON
        return jsonify(questions), 200

    except requests.exceptions.RequestException:
        # Handle network errors with the external API
        return jsonify({"error": "Could not retrieve trivia data from the external API"}), 500
    except Exception as e:
        # Log any unexpected errors for debugging
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/answers', methods=['POST'])
def getting_answers():
    data = request.get_json()
    count = sum(1 for answer, correct in zip(data['answers'], session['correct_answers']) if answer == correct)
    return jsonify({'total': count}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
