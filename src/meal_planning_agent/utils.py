import os

base_system_instructions = '''
You are a meal planning assistant who helps people plan their meals for the week.
You are an expert on simple meals that require minimal amounts of preparation, reheat well, and are delicious.
'''

def assertKeyExists(key :str) -> str:
    value = os.getenv(key)
    if value:
        return value
    raise ValueError(f"{key} not found")

def to_markdown_list(data: list[any], bullet: str ="-"):
    """
    Converts a list into a markdown bulleted list string.
    """
    return "\n".join(f"{bullet} {str(item)}" for item in data)

def filter_out_invalid_strings(input_list: list[str], invalid_strings: set[str]) -> list[str]:
    return [item for item in input_list if item not in invalid_strings]

def clamp(n, min_n, max_n):
    return max(min_n, min(n, max_n))

section_break = "\n\n\n========================================================================================\n\n\n"

def print_break():
    print(section_break)
