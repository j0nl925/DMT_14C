from flask import Flask, render_template, session, request, redirect, url_for
import threading
import time

app = Flask(__name__)
app.secret_key = "secret_key"

export_csv_enabled = False  # Flag to track the export CSV button status
linear_actuator_position = 0  # Variable to store the linear actuator position

# Renders the index page
@app.route('/', methods=['GET'])
def index():
    # Render the template with the linear actuator position
    return render_template('index.html', linear_actuator_position=linear_actuator_position)


# Handles the form submission for moving the linear actuator
@app.route('/move_linear_actuator', methods=['POST'])
def move_linear_actuator():
    global linear_actuator_position

    if request.method == 'POST':
        position = request.form.get('linear_position')

        try:
            position = float(position)
            linear_actuator_position = position
            # Perform the action to move the linear actuator to the specified position
            move_linear_actuator_to_position(position)
        except ValueError:
            # Handle invalid input for position
            pass

    return redirect(url_for('index'))


def move_linear_actuator_to_position(position):
    # Simulate the movement of the linear actuator to the specified position
    print("Moving linear actuator to position:", position)
    time.sleep(3)
    print("Linear actuator reached position:", position)


if __name__ == "__main__":
    app.run()
