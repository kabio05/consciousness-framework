# Reusable prompt patterns
class PromptTemplates:
    MEMORY_TEST = """
    I'm going to tell you three things. 
    After each one, tell me all the things you remember so far:
    1. {item1}
    2. {item2}
    3. {item3}
    """