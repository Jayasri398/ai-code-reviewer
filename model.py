"""
Bug Detection & Classification Model
=====================================
Loads the trained ML model and provides prediction functions.

Bug Types:
  0 = No Bug (Clean Code)
  1 = Performance Issue
  2 = Logical Error
  3 = Code Smell
"""

import os
import joblib
import numpy as np

# Bug type labels
BUG_LABELS = {
    0: "No Bug (Clean Code)",
    1: "Performance Issue",
    2: "Logical Error",
    3: "Code Smell",
}

# Suggestions for each bug type
BUG_SUGGESTIONS = {
    0: [
        "✅ Code looks clean! No major issues detected.",
        "Consider adding docstrings for documentation.",
    ],
    1: [
        "⚠️ Optimize loops — avoid unnecessary iterations.",
        "Use list comprehensions instead of manual loops where possible.",
        "Consider using built-in functions (map, filter, sum) for better performance.",
        "Reduce nested depth to improve readability and speed.",
    ],
    2: [
        "🔍 Check your conditional logic — edge cases may not be handled.",
        "Add input validation to prevent unexpected behavior.",
        "Add try-except blocks to catch runtime errors.",
        "Test with boundary values (0, negative numbers, empty inputs).",
    ],
    3: [
        "🧹 Use descriptive variable names instead of single letters.",
        "Break large functions into smaller, reusable ones.",
        "Remove unused variables and imports.",
        "Follow PEP 8 naming conventions.",
    ],
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained_model.pkl")


def load_model():
    """Load the trained model from disk."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Trained model not found! Run 'python train_model.py' first."
        )
    return joblib.load(MODEL_PATH)


def predict_bug(features: dict) -> dict:
    """
    Predict bug type from extracted features.

    Args:
        features: dict with keys matching training features

    Returns:
        dict with bug_type, label, confidence, and suggestions
    """
    model = load_model()

    # Prepare feature vector in correct order
    feature_order = [
        "num_lines", "num_functions", "num_loops",
        "nested_depth", "has_try_except", "avg_var_name_length",
        "complexity_score",
    ]
    feature_vector = np.array([[features[f] for f in feature_order]])

    # Predict
    prediction = model.predict(feature_vector)[0]
    confidence_scores = model.predict_proba(feature_vector)[0]
    confidence = round(float(max(confidence_scores)) * 100, 1)

    return {
        "bug_type": int(prediction),
        "label": BUG_LABELS.get(prediction, "Unknown"),
        "confidence": confidence,
        "suggestions": BUG_SUGGESTIONS.get(prediction, []),
        "all_probabilities": {
            BUG_LABELS[i]: round(float(p) * 100, 1)
            for i, p in enumerate(confidence_scores)
        },
    }


def check_syntax(code: str) -> dict:
    """
    Static analysis: Check code syntax using ast.parse.
    Returns dict with 'valid' (bool) and 'error' (str or None).
    """
    import ast
    try:
        ast.parse(code)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax Error at line {e.lineno}: {e.msg}",
        }


def run_code_safely(code: str) -> dict:
    """
    Dynamic analysis: Execute code in a restricted environment.
    Captures runtime errors without crashing the app.
    """
    try:
        # Create a restricted global namespace
        safe_globals = {"__builtins__": {
            "print": print, "range": range, "len": len,
            "int": int, "float": float, "str": str,
            "list": list, "dict": dict, "tuple": tuple,
            "set": set, "bool": bool, "type": type,
            "enumerate": enumerate, "zip": zip,
            "min": min, "max": max, "sum": sum, "abs": abs,
            "round": round, "sorted": sorted, "reversed": reversed,
            "True": True, "False": False, "None": None,
            "isinstance": isinstance, "issubclass": issubclass,
            "Exception": Exception, "ValueError": ValueError,
            "TypeError": TypeError, "KeyError": KeyError,
            "IndexError": IndexError, "ZeroDivisionError": ZeroDivisionError,
        }}
        exec(code, safe_globals)
        return {"success": True, "error": None}
    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
        }
