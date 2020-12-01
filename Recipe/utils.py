def break_into_individual(string):
  uncleanArray = string.split(",")
  return uncleanArray

def clean_empty_tags(array):
  cleanArray = []
  for i in range(len(array)):
    print("i: ", array[i])
    if len(array[i]) > 1:
      cleanArray.append(array[i])
  return cleanArray

def clean_whitespace(array):
  cleanArray = []
  for i in range(len(array)):
    tag = ""
    for y in array[i]:
      if y != " ":
        tag += y
    cleanArray.append(tag)
  return cleanArray

def parseTags(string):
  uncleanArray = break_into_individual(string)
  no_empty_tag = clean_empty_tags(uncleanArray)
  final_array = clean_whitespace(no_empty_tag)
  final_string = ""
  for i in range(len(final_array)):
    final_string += final_array[i]
    if i != len(final_array)-1:
        final_string += " "
  return final_string

def ingredient_cleaner(ingredient_string):
    temp_arr, fin, split = [], '', ingredient_string.split(',')
    for i in range(len(split)):
        cleaned_ingr = split[i].lstrip().rstrip()
        if i != len(split) - 1:
            cleaned_ingr += ','
        temp_arr += [cleaned_ingr]
    for ingredient in temp_arr:
        fin += ingredient
    print('fin: ', fin)
    return fin
