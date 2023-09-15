import os
import sys
import random
import spacy
import pandas as pd
from spacy.util import minibatch, compounding

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
from src.database_handler import DatabaseHandler  # wrong-import-position: ignore


print(spacy.__version__)


class CommentEvaluator:
    """Class to get comment and tip data an querry data in batches
    """

    def __init__(self):
        self.__batch_limit = 100000
        self.__offset = 0
        self.__handler = DatabaseHandler()
        self.__query = self.__handler.querry_database
        self.__insert_many = self.__handler.insert_many
        self.__cursor_init = self.__handler.init_fetch_many_cursor
        self.__fetch_batch = self.__handler.fetch_cursor_batch
        self.__create_eval_column()
        print("Ready to go!")

    def __del__(self):
        self.__handler.close_database()

    def get_review_data(self, limit: int = 100000):
        sql = """Select rid, star, text from reviews limit %(limit)s"""
        opt = {"limit": limit}
        data = self.__query(sql, opt)
        df_data = pd.DataFrame(data, columns=["rid", "star", "text"])
        df_data["pos"] = df_data["star"].apply(lambda x: (x >= 3))
        df_data["neg"] = df_data["star"].apply(lambda x: (x < 3))
        df_data["sentiment"] = df_data["star"].apply(lambda x: (x >= 3) * 1)
        return df_data

    def querry_tip_data(self):
        sql = """Select tid, text from tips order by tid::int limit %(limit)s offset %(offset)s"""
        opt = {"limit": self.__batch_limit, "offset": self.__offset}
        data = self.__query(sql, opt)
        df_data = pd.DataFrame(data, columns=["tid", "text"])
        self.__offset += self.__batch_limit
        if len(df_data) == 0:
            self.__offset = 0
        return df_data

    def __create_eval_column(self):
        sql = """ALTER TABLE reviews ADD COLUMN sentiment varchar(20)"""
        try:
            self.__query(sql)
            print('Added column "sentiment" to "reviews"')
        # will throw Exception if col already exists
        except Exception as exep:  # pylint: disable=broad-except
            print(exep)


def add_sentiment_data(df):
    good_words = "love|good|awesome|best|pleasant|nice|good|delicious|favorite|wonderful|amazing|great|nice|helpful"
    bad_words = "horrified|never again|horrible|terrible|very poor|bad|worst|angry|dirty|crappy|overpriced|rip off|scammer|scammers"
    good_mask = df["text"].str.contains(good_words, case=False, regex=True)
    bad_mask = df["text"].str.contains(bad_words, case=False, regex=True)
    df["sentiment"] = "Neutral"
    df["sentiment"][good_mask] = "Good"
    df["sentiment"][bad_mask] = "Bad"


def define_training_data(df: pd.DataFrame, split: float = 0.8, limit: int = 0) -> tuple:
    reviews = []
    for _, review in df.iterrows():
        text = review["text"]
        text = text.replace("<br />", "\n\n")
        if text.strip():
            spacy_label = {
                "cats": {
                    "pos": review["pos"],
                    "neg": review["neg"],
                }
            }
            reviews.append((text, spacy_label))
    random.shuffle(reviews)

    if limit:
        reviews = reviews[:limit]
    split = int(len(reviews) * split)
    return reviews[:split], reviews[split:]


def evaluate_model(tokenizer, textcat, test_data: list) -> dict:
    reviews, labels = zip(*test_data)
    reviews = (tokenizer(review) for review in reviews)
    true_positives = 0
    false_positives = 1e-8  # Can't be 0 because of presence in denominator
    true_negatives = 0
    false_negatives = 1e-8
    for i, review in enumerate(textcat.pipe(reviews)):
        true_label = labels[i]["cats"]
        for predicted_label, score in review.cats.items():
            # Every cats dictionary includes both labels. You can get all
            # the info you need with just the pos label.
            if predicted_label == "neg":
                continue
            if score >= 0.5 and true_label["pos"]:
                true_positives += 1
            elif score >= 0.5 and true_label["neg"]:
                false_positives += 1
            elif score < 0.5 and true_label["neg"]:
                true_negatives += 1
            elif score < 0.5 and true_label["pos"]:
                false_negatives += 1
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)

    if precision + recall == 0:
        f_score = 0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {"precision": precision, "recall": recall, "f-score": f_score}


def train_model(training_data: list, test_data: list, iterations: int = 20) -> None:
    # Build pipeline
    nlp = spacy.load("en_core_web_sm")
    if "textcat" not in nlp.pipe_names:
        textcat = nlp.create_pipe("textcat", config={"architecture": "simple_cnn"})
        nlp.add_pipe(textcat, last=True)
    else:
        textcat = nlp.get_pipe("textcat")

    textcat.add_label("pos")
    textcat.add_label("neg")

    # Train only textcat
    training_excluded_pipes = [pipe for pipe in nlp.pipe_names if pipe != "textcat"]

    with nlp.disable_pipes(training_excluded_pipes):
        optimizer = nlp.begin_training()
        # Training loop
        print("Beginning training")
        print("Iteration\tLoss\tPrecision\tRecall\tF-score")
        batch_sizes = compounding(4.0, 32.0, 1.001)  # A generator that yields infinite series of input numbers
        for i in range(iterations):
            loss = {}
            random.shuffle(training_data)
            batches = minibatch(training_data, size=batch_sizes)
            for batch in batches:
                text, labels = zip(*batch)
                nlp.update(text, labels, drop=0.2, sgd=optimizer, losses=loss)
            with textcat.model.use_params(optimizer.averages):
                evaluation_results = evaluate_model(
                    tokenizer=nlp.tokenizer,
                    textcat=textcat,
                    test_data=test_data
                )
                print(
                    f"{i}:\t\t{loss['textcat']:.4f}\t{evaluation_results['precision']:.5f}"
                    f"\t\t{evaluation_results['recall']:.5f}"
                    f"\t{evaluation_results['f-score']:.5f}"
                )
    # Save model
    with nlp.use_params(optimizer.averages):
        nlp.to_disk("model_artifacts")


def test_model(loaded_model, input_data: str, printdata=False):
    # Generate prediction
    parsed_text = loaded_model(input_data)
    # Determine prediction to return
    if parsed_text.cats["pos"] > parsed_text.cats["neg"]:
        prediction = "Positive"
        score = parsed_text.cats["pos"]
    else:
        prediction = "Negative"
        score = parsed_text.cats["neg"]
    if printdata:
        print(
            f"Review text: {input_data}\nPredicted sentiment: {prediction}"
            f"\tScore: {score}"
        )
    return [prediction, score]


def predict_tips(comment_evaluator):
    tip_df = comment_evaluator.querry_tip_data()

    loaded_model = spacy.load("model_artifacts")
    db_handler = DatabaseHandler()
    sql = """ALTER TABLE tips ADD COLUMN sentiment varchar(20), ADD COLUMN score DECIMAL(10,9)"""
    try:
        db_handler.querry_database(sql)
        print('Added column "sentiment" and "score" to "tips"')
    except Exception as exep:  # pylint: disable=broad-except
        print(exep)

    sql_insert = """UPDATE tips
    set sentiment = data.sentiment,
    score = data.score
    from (values %s) as data (tid, sentiment, score)
    where tips.tid = data.tid::CHAR(22)
    """

    fetched_batch = 1

    while len(tip_df) != 0:
        print(f"--- Estimating for batch no. {fetched_batch} ---")

        total_data = len(tip_df)
        steps = int(total_data / 100)
        tenths = int(total_data / 10)

        calculated_data = []

        for number, (_, row) in enumerate(tip_df.iterrows()):
            if number % tenths == 0:
                print(f"{number/total_data*100:.0f}", end="")
            elif number % steps == 0:
                print(".", end="")
            prediction, score = test_model(loaded_model, row["text"])
            calculated_data.append((row["tid"], prediction, score,))

        print("\n")
        db_handler.insert_many(sql_insert, calculated_data)

        tip_df = comment_evaluator.querry_tip_data()
        fetched_batch += 1

    print("done!")


if __name__ == "__main__":
    ce = CommentEvaluator()
    rdf = ce.get_review_data()

    TESTTEXT = 'Great place!  We went at night and the place was bouncing with people... Mostly a young crowd.. Not a family place at night.. More like a night club.  We went for food,  ordered the carne asada street tacos,  and the Jefe Burger.  Both just perfect.  The tacos were at point,  juicy seasoned meat on small corn tortillas.  The meat on the Burger was tender and pretty juicy. Friendly staff. I would return!'

    train, test = define_training_data(rdf, limit=20000)
    train_model(train, test)

    print("Testing model")
    model = spacy.load("model_artifacts")
    test_model(model, TESTTEXT, True)

    predict_tips(ce)
