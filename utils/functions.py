def clossing_index(word: str) -> int:
    c = 1
    for i in range(1, len(word)):
        if word[i] == '(':
            c += 1
        elif word[i] == ')':
            c -= 1
        if c == 0:
            return i
    return -1