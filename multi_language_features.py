import re

def extract_general_features(code, language):

    features = {}

    lines = code.split("\n")
    features["num_lines"] = len(lines)

    # Detect loops (common in all languages)
    features["num_loops"] = len(re.findall(r"\b(for|while)\b", code))

    # Detect functions (basic patterns for multiple languages)
    if language == "Python":
        features["num_functions"] = len(re.findall(r"\bdef\b", code))
    elif language == "Java":
        features["num_functions"] = len(re.findall(r"\b(public|private|protected)\b", code))
    elif language == "C++":
        features["num_functions"] = len(re.findall(r"\b(int|void|float|double|string)\b", code))
    elif language == "JavaScript":
        features["num_functions"] = len(re.findall(r"\bfunction\b", code))
    else:
        features["num_functions"] = 0

    # Try-catch detection
    features["has_try_except"] = bool(
        re.search(r"\b(try|catch|except)\b", code)
    )

    # Simple nesting approximation
    features["nested_depth"] = code.count("{")

    # Dummy variable length estimate
    features["avg_var_name_length"] = 5

    # Simple complexity score
    complexity = features["num_loops"] + features["num_functions"]
    features["complexity_score"] = min(10, complexity)

    return features
