from sklearn.datasets import load_iris
import numpy as np
import matplotlib.pyplot as plt


#----------------------------MODEL STUFF---------------------------------

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

    # PHASE 1: FORWARD PASS
    input_with_bias = np.concatenate(([1], point)) 

    hidden_raw = np.dot(hidden_weights, input_with_bias)
    hidden_output = sigmoid(hidden_raw)

    hidden_with_bias = np.concatenate(([1], hidden_output)) 

    output_raw = output_raw = np.dot(output_weights, hidden_with_bias)
    final_output = sigmoid(output_raw)


    # BACKWARD PASS
    output_error = target_label - final_output
    output_delta = output_error * (final_output * (1 - final_output))

    hidden_errors = np.dot(output_weights[:, 1:].T, output_delta)
    hidden_deltas = hidden_errors * (hidden_output * (1 - hidden_output))

    output_weights += learning_rate * np.outer(output_delta, hidden_with_bias)

    hidden_weights += learning_rate * np.outer(hidden_deltas, input_with_bias)

    return hidden_weights, output_weights


# to be used looping over many eras
def epoch(hidden_weights, output_weights, training_set, training_labels, learning_rate):

    for point, label in zip(training_set, training_labels):

        hidden_weights, output_weights = train(hidden_weights, output_weights, point, label, learning_rate)

    return hidden_weights, output_weights


# final eval
def evaluate(hidden_weights, output_weights, testing_set, testing_labels):

    correct = 0

    for point, label in zip(testing_set, testing_labels):

        prediction = np.argmax(predict(hidden_weights, output_weights, point))
        label = np.argmax(label)

        if prediction == label:
            correct += 1

    return correct / len(testing_set)



#--------------------------------DATA STUFF--------------------------------------
iris = load_iris()
X = iris.data
y = iris.target

# claude pointed me to google which pointed me to one hot encoding
# to help w/ classification
y_onehot = np.eye(3)[y]

# shuffle data
indices = np.random.permutation(150)
X = X[indices]
y_onehot = y_onehot[indices]



#-----------------------------------LEARNING---------------------------
# train/test split
training_set = X[:120]
training_labels = y_onehot[:120]
testing_set = X[120:]
testing_labels = y_onehot[120:]

num_hidden = 6
learning_rate = 0.1
num_epochs = 500

hidden_weights = np.random.uniform(-1, 1, (num_hidden, training_set.shape[1] + 1))
output_weights = np.random.uniform(-1, 1, (3, num_hidden + 1))

# store error at each epoch
errors = []

# training loop
for i in range(num_epochs):
    hidden_weights, output_weights = epoch(hidden_weights, output_weights, training_set, training_labels, learning_rate)

    total_error = 0
    for point, label in zip(training_set, training_labels):
        output = predict(hidden_weights, output_weights, point)
        total_error += np.mean((label - output) ** 2)
    errors.append(total_error / len(training_set))

# plotting
plt.plot(errors)
plt.xlabel("Epoch")
plt.ylabel("Average Error")
plt.title("Training Error over Time")
plt.savefig('iris_training_error.png')
plt.show()


# eval
accuracy = evaluate(hidden_weights, output_weights, testing_set, testing_labels)
print(f"Accuracy: {accuracy}")