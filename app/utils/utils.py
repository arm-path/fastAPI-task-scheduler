def camel_case_to_snake_case(camel_case_string):
    snake_case_string = ""
    for i, c in enumerate(camel_case_string):
        if i > 0 and c.isupper():
            snake_case_string += "_"
        snake_case_string += c.lower()
    return snake_case_string

