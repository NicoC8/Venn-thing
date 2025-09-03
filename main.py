from random import choice
import random
sentence = input("Sentence:  ")
while True:
  list = sentence.split(" ")
  option = int(input("What would you like to do with the list?\nRandom word - 1\nSort the list - 2\nAdd a word to the list - 3\nPrint each element of the list - 4\nSearch the list for a word - 5\n"))
  if option == 1:
    word = random.choice(list)
    print(word)
  elif option == 2:
    list.sort()
    print(list)
  elif option == 3:
    list.append(input("What word do you want to add?  "))
    print(list)
  elif option == 4:
    for i in range(len(list)):
      print(list[i])
  elif option == 5:
    search = input("What word do you want to search for?  ")
    try:
      print(search, "is in the list, index: ", list.index(search))
    except:
      print("That word is not in the list")