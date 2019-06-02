import jsonlines
from pyfiglet import print_figlet


print_figlet("Main Json Handler")
print()
filename = input("Enter the file name: ")
first_label = input("Enter the first label: ")
second_label = input("Enter the second label: ")
print()

total_first_label_count = 0
total_second_label_count = 0

with jsonlines.open(filename, "r") as reader:
    for line in reader:
        if line["label"] == first_label:
            total_first_label_count += 1
        elif line["label"] == second_label:
            total_second_label_count += 1
        else:
            print("Error")

print("Total first label: " + str(total_first_label_count))
print("Total second label: " + str(total_second_label_count))
print()
print("How many training data required? ")
training_data_num = int(input("> "))
print("How many testing data required? ")
testing_data_num = int(input("> "))
print("The other data will become testing data during development!!")

first_label_count = 0
second_label_count = 0
with jsonlines.open(filename, "r") as reader:
    for line in reader:
        if line["label"] == first_label and first_label_count < training_data_num:
            first_label_count += 1
            with jsonlines.open("train.jsonl", "a") as writer:
                writer.write(line)
        elif line["label"] == second_label and second_label_count < training_data_num:
            second_label_count += 1
            with jsonlines.open("train.jsonl", "a") as writer:
                writer.write(line)
        elif line["label"] == first_label and first_label_count < training_data_num + testing_data_num:
            first_label_count += 1
            with jsonlines.open("test.jsonl", "a") as writer:
                writer.write(line)
        elif line["label"] == second_label and second_label_count < training_data_num + testing_data_num:
            second_label_count += 1
            with jsonlines.open("test.jsonl", "a") as writer:
                writer.write(line)
        else:
            with jsonlines.open("devTest.jsonl", "a") as writer:
                writer.write(line)

print()
with open("log", "w") as f:
    f.write("Information\n")
    f.write("----------------------------------\n")
    f.write("File: train.jsonl\n")
    f.write("prepaid number: " + str(training_data_num) + "\n")
    f.write("postpaid number: " + str(training_data_num) + "\n\n")
    f.write("File: test.jsonl\n")
    f.write("prepaid number: " + str(testing_data_num) + "\n")
    f.write("postpaid number: " + str(testing_data_num) + "\n\n")
    f.write("File: devTest.jsonl\n")
    f.write("prepaid number: " + str(total_first_label_count - training_data_num - testing_data_num) + "\n")
    f.write("postpaid number: " + str(total_second_label_count - training_data_num - testing_data_num) + "\n")
