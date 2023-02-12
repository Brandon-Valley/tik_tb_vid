str = "honey, I'm worried."

def cap_only_1st_letter_of_str(in_str):
    if len(in_str) == 0:
        raise ValueError(f"{len(in_str)=}, should not be possible")
    elif len(in_str) == 1:
        return str.capitalize()
    else:
        return str[0].capitalize() + str[1:]
    

# str = str[0].capitalize() + str[1:]
print(cap_only_1st_letter_of_str(str))