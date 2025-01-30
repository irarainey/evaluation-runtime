import logging
from azure.ai.evaluation import (
    F1ScoreEvaluator,
    BleuScoreEvaluator,
    RougeScoreEvaluator,
    RougeType,
    GleuScoreEvaluator,
    MeteorScoreEvaluator,
)


def calculate_f1(data):
    """
    Calculate the F1 score for the model output.

    Parameters:
    - data (dict): The data to evaluate.

    Returns:
    - dict: The evaluation results.
    """
    logging.info("Evaluating using F1 Score")
    evaluator = F1ScoreEvaluator()
    result = evaluator(**data)
    return result


def calculate_bleu(data):
    """
    Calculate the BLEU score for the model output.

    Parameters:
    - data (dict): The data to evaluate.

    Returns:
    - dict: The evaluation results.
    """
    logging.info("Evaluating using BLEU Score")
    evaluator = BleuScoreEvaluator()
    result = evaluator(**data)
    return result


def calculate_rouge(data):
    """
    Calculate the ROUGE score for the model output.

    Parameters:
    - data (dict): The data to evaluate.

    Returns:
    - dict: The evaluation results.
    """
    logging.info("Evaluating using ROUGE Score")
    rouge_score_evaluator = RougeScoreEvaluator(RougeType.ROUGE_1)
    result = rouge_score_evaluator(**data)
    return result


def calculate_gleu(data):
    """
    Calculate the GLEU score for the model output.

    Parameters:
    - data (dict): The data to evaluate.

    Returns:
    - dict: The evaluation results.
    """
    logging.info("Evaluating using GLEU Score")
    rouge_score_evaluator = GleuScoreEvaluator()
    result = rouge_score_evaluator(**data)
    return result


def calculate_meteor(data):
    """
    Calculate the METEOR score for the model output.

    Parameters:
    - data (dict): The data to evaluate.

    Returns:
    - dict: The evaluation results.
    """
    logging.info("Evaluating using METEOR Score")
    rouge_score_evaluator = MeteorScoreEvaluator()
    result = rouge_score_evaluator(**data)
    return result


evaluator_functions = {
    "f1": calculate_f1,
    "bleu": calculate_bleu,
    "rouge": calculate_rouge,
    "gleu": calculate_gleu,
    "meteor": calculate_meteor,
}


def evaluate(evaluators, data) -> dict:
    """
    Evaluate the model output using the specified evaluators.

    Parameters:
    - evaluators (list): A list of evaluators to use.
    - data (dict): The data to evaluate.

    Returns:
    - dict: The evaluation results.
    """
    results = {}
    for evaluator in evaluators:
        func = evaluator_functions.get(evaluator)
        if func:
            # Call the evaluator function and store the result
            result = func(data)
            if evaluator == "rouge":
                results[evaluator] = result
            else:
                results[evaluator] = result[f"{evaluator}_score"]
        else:
            print(f"Warning: No function defined for evaluator '{evaluator}'")
    return results
