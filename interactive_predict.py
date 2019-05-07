import traceback

from common import common
from extractor import Extractor

SHOW_TOP_CONTEXTS = 10
MAX_PATH_LENGTH = 8
MAX_PATH_WIDTH = 2
JAR_PATH = 'JavaExtractor/JPredict/target/JavaExtractor-0.0.1-SNAPSHOT.jar'


class InteractivePredictor:
    exit_keywords = ['exit', 'quit', 'q']

    def __init__(self, config, model):
        model.predict([])
        self.model = model
        self.config = config
        self.path_extractor = Extractor(config,
                                        jar_path=JAR_PATH,
                                        max_path_length=MAX_PATH_LENGTH,
                                        max_path_width=MAX_PATH_WIDTH)

    def read_file(self, input_filename):
        with open(input_filename, 'r') as file:
            return file.readlines()

    def predict(self):
        input_filename = 'Input.java'
        print('Starting interactive prediction...')
        while True:
            print(
                'Modify the file: "%s" and press any key when ready, or "q" / "quit" / "exit" to exit' % input_filename)
            user_input = input()
            if user_input.lower() in self.exit_keywords:
                print('Exiting...')
                return
            try:
                print("input_filename(ohazyi) = ", input_filename)
                predict_lines, hash_to_string_dict = self.path_extractor.extract_paths(input_filename)
                print("predict_lines(ohazyi) = ", predict_lines)
                print("hash_to_string_dict(ohazyi) = ", hash_to_string_dict)
            except ValueError as e:
                print(e)
                continue
            results, code_vectors = self.model.predict(predict_lines)
            print('results(ohazyi)=', results)
            print('code_vectors(ohazyi)', code_vectors)
            import numpy as np
            print("code_vectors(ohazyi).shape", np.array(code_vectors).shape)
            prediction_results = common.parse_results(results, hash_to_string_dict, topk=SHOW_TOP_CONTEXTS)
            print("prediction_results(ohazyi)=", prediction_results)
            for i, method_prediction in enumerate(prediction_results):
                print("i=", i)
                print('Original name:\t' + method_prediction.original_name)
                for name_prob_pair in method_prediction.predictions:
                    print('\t(%f) predicted: %s' % (name_prob_pair['probability'], name_prob_pair['name']))
                print('Attention:')
                for attention_obj in method_prediction.attention_paths:
                    print('%f\tcontext: %s,%s,%s' % (
                    attention_obj['score'], attention_obj['token1'], attention_obj['path'], attention_obj['token2']))
                if self.config.EXPORT_CODE_VECTORS:
                    print("Yes(ohazyi)!!!")
                    print('Code vector:')
                    print(' '.join(map(str, code_vectors[i])))
