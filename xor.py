"""
practice with  backpropagation
"""
import numpy as np
import math


#------------------------------- MODEL STUFF -------------------------------------------

# single spot to handle sigmoid calculations
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# does initial pass thru and classification prediction
def predict(hidden_weights, output_weights, point):

    input_with_bias = np.concatenate(([1],point))

    hidden_raw = np.dot(hidden_weights, input_with_bias)

    hidden_output = sigmoid(hidden_raw)

    hidden_input = np.concatenate(([1],hidden_output)) 

    output_raw = np.dot(output_weights, hidden_input)
    final_output = sigmoid(output_raw)

    return final_output


# training function
def train(hidden_weights, output_weights, point, target_label, learning_rate):

    # FORWARD PASS
    input_with_bias = np.concatenate(([1], point)) 

    hidden_raw = np.dot(hidden_weights, input_with_bias)
    hidden_output = sigmoid(hidden_raw)

    hidden_with_bias = np.concatenate(([1], hidden_output)) 

    output_raw = np.dot(output_weights, hidden_with_bias)
    final_output = sigmoid(output_raw)


    # BACKWARD PASS
    output_error = target_label - final_output
    output_delta = output_error * (final_output * (1 - final_output))

    hidden_errors = output_delta * output_weights[1:]
    hidden_deltas = hidden_errors * (hidden_output * (1 - hidden_output))

    output_weights += learning_rate * output_delta * hidden_with_bias

    hidden_weights += learning_rate * np.outer(hidden_deltas, input_with_bias)

    return hidden_weights, output_weights


# to be used looping over many eras
def epoch(hidden_weights, output_weights, training_set, training_labels, learning_rate):

    for point, label in zip(training_set, training_labels):
        hidden_weights, output_weights = train(hidden_weights, output_weights, point, label, learning_rate)

    return hidden_weights, output_weights


# final evaluation
def evaluate(hidden_weights, output_weights, testing_set, testing_labels):

    correct = 0

    for point, label in zip(testing_set, testing_labels):

        prediction = predict(hidden_weights, output_weights, point)

        if round(prediction) == label:
            correct += 1

    return correct / len(testing_set)




#------------------------------ XOR STUFF ----------------------------------------
# XOR dataset
training_set = np.array([[0,0], [0,1], [1,0], [1,1]])
training_labels = np.array([0, 1, 1, 0])


#------------------------------LEARNING----------------------------
num_hidden = 4
learning_rate = 0.1
num_epochs = 10000

hidden_weights = np.random.uniform(-1, 1, (num_hidden, training_set.shape[1] + 1))
output_weights = np.random.uniform(-1, 1, num_hidden + 1)

# trainig loop
for i in range(num_epochs):
    hidden_weights, output_weights = epoch(hidden_weights, output_weights, training_set, training_labels, learning_rate)

# eval
accuracy = evaluate(hidden_weights, output_weights, training_set, training_labels)
print(f"Accuracy: {accuracy}")

# printing model predictions for debug
for point, label in zip(training_set, training_labels):
    prediction = predict(hidden_weights, output_weights, point)
    print(f"Input: {point}, Target: {label}, Output: {round(prediction, 3)}, Predicted: {round(prediction)}")